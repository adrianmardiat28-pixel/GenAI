# backend/chat_ai_api.py
# pyrefly: ignore [missing-import]
import json, httpx, traceback
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from typing import Optional, List, Dict
from database import fetch_data

router = APIRouter()
GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

DB_CONFIG = {
    "dbname": "dvdrental",
    "user": "postgres",
    "password": "adrian280406",
    "host": "localhost",
    "port": "5432"
}

chat_history: List[Dict[str, str]] = []


def get_db_schema_summary():
    """Return a concise description of the dvdrental schema for the LLM."""
    return """
DATABASE SCHEMA (PostgreSQL — dvdrental):
Tables:
  • film (film_id, title, description, release_year, language_id, rental_duration, rental_rate, length, replacement_cost, rating, special_features, fulltext)
  • category (category_id, name)
  • film_category (film_id, category_id)
  • actor (actor_id, first_name, last_name, last_update)
  • film_actor (actor_id, film_id, last_update)
  • inventory (inventory_id, film_id, store_id, last_update)
  • rental (rental_id, rental_date, inventory_id, customer_id, return_date, staff_id, last_update)
  • payment (payment_id, customer_id, staff_id, rental_id, amount, payment_date)
  • customer (customer_id, store_id, first_name, last_name, email, address_id, activebool, create_date, last_update, active)
  • store (store_id, manager_staff_id, address_id, last_update)
  • staff (staff_id, first_name, last_name, address_id, email, store_id, active, username, password, last_update, picture)
  • address (address_id, address, address2, district, city_id, postal_code, phone, last_update)
  • city (city_id, city, country_id, last_update)
  • country (country_id, country, last_update)
  • language (language_id, name, last_update)

Common JOINs:
  film → film_category → category (for genre)
  film → film_actor → actor (for cast)
  film → inventory → rental → payment (for revenue)
  customer → address → city → country (for geography)
"""


def execute_safe_query(sql: str):
    """Execute a SELECT-only query and return results as list of dicts."""
    sql_clean = sql.strip().rstrip(";").strip()
    
    # Safety: only allow SELECT queries
    if not sql_clean.upper().startswith("SELECT"):
        return {"error": "Hanya query SELECT yang diperbolehkan."}
        
    # Safety: block dangerous keywords
    dangerous = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "TRUNCATE", "CREATE", "GRANT", "REVOKE"]
    for kw in dangerous:
        if kw in sql_clean.upper().split():
            return {"error": f"Query mengandung keyword berbahaya: {kw}"}
            
    # --- PERBAIKAN BUG LIMIT ---
    # Cek apakah query dari AI sudah memiliki batas LIMIT sendiri
    if "LIMIT" not in sql_clean.upper():
        sql_clean += " LIMIT 500"
        
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Eksekusi query dengan menambahkan titik koma di akhir
        cur.execute(sql_clean + ";")
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        # Convert Decimal/date to JSON-safe types
        result = []
        for row in rows:
            clean_row = {}
            for k, v in dict(row).items():
                if hasattr(v, '__float__'):
                    clean_row[k] = float(v)
                elif hasattr(v, 'isoformat'):
                    clean_row[k] = v.isoformat()
                else:
                    clean_row[k] = v
            result.append(clean_row)
        return result
    except Exception as e:
        return {"error": str(e)}

class AIChatRequest(BaseModel):
    prompt: str
    existing_charts: Optional[List[Dict]] = None  # Current charts on page for context


@router.post("/chat-ai")
async def chat_ai(request: AIChatRequest):
    global chat_history

    schema = get_db_schema_summary()
    
    # Build context about existing charts — use 0-based index consistently
    existing_charts_info = ""
    if request.existing_charts and len(request.existing_charts) > 0:
        existing_charts_info = "\n\nCHART YANG SAAT INI DITAMPILKAN DI HALAMAN (gunakan chart_index 0-based):"
        for i, chart in enumerate(request.existing_charts):
            existing_charts_info += f"\n  chart_index={i}: \"{chart.get('title', 'Untitled')}\" (type: {chart.get('type', '?')})"
            if chart.get('colors'):
                existing_charts_info += f" — warna saat ini: {json.dumps(chart.get('colors')[:5])}"

    system_instruction = (
        "Kamu adalah 'AI Data Analyst', seorang analis data senior yang sangat cerdas untuk DVD Rental Database milik Adrian. "
        "Tugasmu adalah menerima pertanyaan dalam bahasa natural, lalu:\n"
        "1. Menulis SQL query yang tepat untuk menjawab pertanyaan\n"
        "2. Menghasilkan spesifikasi chart Plotly.js untuk memvisualisasikan data\n"
        "3. Memberikan analisis mendalam tentang data\n"
        "4. Mengubah warna chart atau tema halaman jika diminta\n"
        f"\n{schema}"
        f"{existing_charts_info}"

        "\n\n=== ATURAN UTAMA ==="
        "\n1. SELALU tulis SQL query yang valid untuk PostgreSQL dvdrental database."
        "\n2. HANYA gunakan SELECT query (tidak boleh INSERT/UPDATE/DELETE/DROP)."
        "\n3. Berikan analisis mendalam: tren, insight bisnis, rekomendasi."
        "\n4. JANGAN membuat data palsu — semua data harus dari query SQL."
        "\n5. Jawab dalam bahasa yang sama dengan user."
        "\n6. FOKUS PADA PERMINTAAN: HANYA hasilkan chart yang secara eksplisit diminta pada prompt terakhir user. JANGAN membuat chart tambahan, JANGAN menebak chart lain, dan JANGAN mengulang chart dari obrolan sebelumnya."

        "\n\n=== FITUR GANTI WARNA (PENTING!) ==="
        "\nJika user minta ganti warna chart (misal: 'ganti warna jadi merah', 'ubah warna chart pertama', 'warna biru'):"
        "\n• WAJIB isi field 'chart_updates' dengan array yang berisi objek {chart_index, new_colors}"
        "\n• chart_index = 0 untuk chart pertama, 1 untuk kedua, dst (0-BASED INDEX!)"
        "\n• new_colors = array warna hex, minimal 5-10 warna"
        "\n• Jika user bilang 'semua chart', buat entry untuk setiap chart_index"
        "\n• Jika user bilang 'chart pertama', chart_index = 0"
        "\n• Jika user bilang 'chart kedua', chart_index = 1"
        "\n• Contoh warna: merah=['#ef4444','#dc2626','#f87171','#fca5a5','#b91c1c']"
        "\n• Contoh warna: biru=['#3b82f6','#2563eb','#60a5fa','#93c5fd','#1d4ed8']"
        "\n• Contoh warna: hijau=['#22c55e','#16a34a','#4ade80','#86efac','#15803d']"
        "\n• Contoh warna: ungu=['#8b5cf6','#7c3aed','#a78bfa','#c4b5fd','#6d28d9']"
        "\n• Contoh warna: orange=['#f97316','#ea580c','#fb923c','#fdba74','#c2410c']"
        "\n• Contoh warna: pink=['#ec4899','#db2777','#f472b6','#f9a8d4','#be185d']"
        "\n• Contoh warna: kuning=['#eab308','#ca8a04','#facc15','#fde047','#a16207']"
        "\n• Contoh colorful/rainbow=['#ef4444','#f97316','#eab308','#22c55e','#3b82f6','#8b5cf6','#ec4899','#14b8a6','#f43f5e','#6366f1']"

        "\n\n=== FITUR GANTI WARNA / TEMA ==="
        "\n- Jika user minta ganti warna chart, isi array 'chart_updates' dengan {chart_index: 0, new_colors: ['#hex1', ...]}. Jika tidak, biarkan kosong []."
        "\n- Jika user minta ganti tema halaman, isi objek 'page_theme'. Jika tidak, isi null."
        "\n• Isi field 'page_theme' dengan objek berisi:"
        "\n  - bg_color: warna CSS background (contoh: '#0a0e1a', '#1e1b4b', '#0f172a', '#18181b', '#1a1a2e', '#ffffff')"
        "\n  - accent_color: warna CSS accent (contoh: '#6366f1', '#ec4899', '#22c55e', '#f97316')"
        "\n  - text_color: warna CSS text (contoh: '#e2e8f0' untuk gelap, '#1e293b' untuk terang)"
        "\n• Jika TIDAK diminta ganti tema, page_theme harus null"

        "\n\n=== FORMAT RESPONS WAJIB (VALID JSON) ==="
        "\n{"
        "\n  \"message\": \"Analisis data langsung pada intinya...\","
        "\n  \"charts\": ["
        "\n    {"
        "\n      \"title\": \"Judul Chart\","
        "\n      \"type\": \"bar|line|pie|scatter\","
        "\n      \"sql\": \"SELECT ...\","
        "\n      \"x_column\": \"nama_kolom_x\","
        "\n      \"y_column\": \"nama_kolom_y\","
        "\n      \"colors\": [\"#hex1\", \"#hex2\"],"
        "\n      \"layout_options\": {}"
        "\n    }"
        "\n  ],"
        "\n  \"chart_updates\": [],"
        "\n  \"page_theme\": null"
        "\n}"
        "\n\nNOTE:"
        "\n- 'charts' = chart BARU. Kosong [] jika tidak perlu chart baru."
        "\n- 'chart_updates' = update warna chart yang SUDAH ADA. Kosong [] jika tidak ada update. HARUS isi jika user minta ganti warna!"
        "\n- 'page_theme' = ubah tema halaman. null jika tidak diminta."
        "\n- 'message' WAJIB ada dan berisi penjelasan."
        "\n- Untuk pie chart: x_column = label column, y_column = value column."
        "\n- SELALU beri colors yang cantik dan harmonis untuk chart baru."
    )

    # Build messages
    messages = [{"role": "system", "content": system_instruction}]
    messages.extend(chat_history[-6:])
    messages.append({"role": "user", "content": request.prompt})

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": messages,
                    "response_format": {"type": "json_object"},
                    "temperature": 0.3,
                    "max_tokens": 4096
                }
            )

            res_data = response.json()
            print(f"[AI Page] Groq status: {response.status_code}")

            if response.status_code != 200 or 'error' in res_data:
                error_msg = res_data.get('error', {}).get('message', f'HTTP {response.status_code}')
                print(f"[AI Page] Groq Error: {error_msg}")
                return {"message": f"⚠️ AI Error: {error_msg}", "charts": [], "chart_updates": []}

            if 'choices' not in res_data or len(res_data['choices']) == 0:
                return {"message": "⚠️ AI tidak memberikan respons. Coba lagi.", "charts": [], "chart_updates": []}

            raw_content = res_data['choices'][0]['message']['content']
            print(f"[AI Page] Response length: {len(raw_content)} chars")
            print(f"[AI Page] Response preview: {raw_content[:500]}")

            try:
                ai_content = json.loads(raw_content)
            except json.JSONDecodeError:
                ai_content = {"message": raw_content, "charts": [], "chart_updates": []}

            ai_message = ai_content.get('message', 'Analisis selesai.')
            ai_charts = ai_content.get('charts', [])
            ai_chart_updates = ai_content.get('chart_updates', [])
            ai_page_theme = ai_content.get('page_theme', None)

            # Execute SQL for each chart and attach the data
            charts_with_data = []
            for chart_spec in ai_charts:
                sql = chart_spec.get('sql', '')
                if sql:
                    query_result = execute_safe_query(sql)
                    if isinstance(query_result, dict) and 'error' in query_result:
                        ai_message += f"\n\n[WARN] Query error untuk chart '{chart_spec.get('title', '?')}': {query_result['error']}"
                    else:
                        chart_spec['data'] = query_result
                        charts_with_data.append(chart_spec)
                else:
                    charts_with_data.append(chart_spec)

            # Save to history
            if len(str(ai_message)) > 20:
                chat_history.append({"role": "user", "content": request.prompt})
                chat_history.append({"role": "assistant", "content": str(ai_message)[:500]})

            return {
                "message": ai_message,
                "charts": charts_with_data,
                "chart_updates": ai_chart_updates or [],
                "page_theme": ai_page_theme
            }

    except Exception as e:
        traceback.print_exc()
        return {"message": f"🔴 Backend Error: {str(e)}", "charts": [], "chart_updates": []}