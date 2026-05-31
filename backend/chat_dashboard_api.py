import os
import json
import httpx
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict
import traceback

router = APIRouter()

GROQ_API_KEY = "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" # API Key milikmu
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

chat_history: List[Dict[str, str]] = []

DB_CONFIG = {
    "dbname": "dvdrental",
    "user": "postgres",
    "password": "adrian280406", 
    "host": "localhost",
    "port": "5432"
}

class DashboardChatRequest(BaseModel):
    prompt: str
    dashboard_context: str

def get_dashboard_db_intel():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("SELECT SUM(amount) as total_revenue FROM payment")
        rev = cur.fetchone()
        cur.execute("SELECT COUNT(*) as total FROM film")
        films = cur.fetchone()
        
        cur.execute("SELECT rating, ROUND(AVG(length), 1) as avg_duration FROM film GROUP BY rating ORDER BY avg_duration DESC")
        chart_data = cur.fetchall()
        
        cur.close()
        conn.close()
        
        formatted_chart_data = []
        for row in chart_data:
            formatted_row = dict(row)
            if 'avg_duration' in formatted_row and formatted_row['avg_duration'] is not None:
                formatted_row['avg_duration'] = float(formatted_row['avg_duration'])
            formatted_chart_data.append(formatted_row)
        
        return {
            "revenue": float(rev['total_revenue']) if rev['total_revenue'] else 0.0, 
            "total_film": films['total'],
            "data_diagram_durasi_rating": formatted_chart_data
        }
    except Exception as e:
        return {"error": str(e)}

@router.post("/chat-dashboard")
async def chat_dashboard(request: DashboardChatRequest):
    global chat_history
    db_data = get_dashboard_db_intel()
    
# SYSTEM PROMPT: BESI BAJA (Anti-Out-of-Context & Anti-Halusinasi UI)
    system_instruction = (
        "Kamu adalah AI Assistant eksklusif untuk 'Movie Inventory Dashboard' milik Adrian Alrizqullah Mardiat. "
        "Tugasmu adalah membantu user dengan 6 fitur utama sambil menjaga kualitas respons dan UI integrity."
        f"\n\n--- DATABASE & KONTEKS ---\n{json.dumps(db_data)}"
        
        "\n\n🚨 ATURAN MUTLAK 1: PEMBATASAN KONTEKS 🚨"
        "\nKamu HANYA BOLEH membahas data film, UI dashboard, dan analisis diagram."
        "\nJIKA user bertanya hal di luar konteks (buah, hewan, dll), TOLAK dengan sopan."

        "\n\n🚨 ATURAN MUTLAK 2: ANTI-HALUSINASI UI (SANGAT KETAT) 🚨"
        "\nJANGAN PERNAH merubah nilai UI (warna, posisi, filter, diagram) JIKA TIDAK ADA PERINTAH EKSPLISIT DARI USER!"
        "\nJika user HANYA bertanya data (misal: 'berapa total film?', 'film apa yang paling lama?'), MAKA SEMUA NILAI LAYOUT WAJIB null!"

        "\n\n📋 FITUR 1: UBAH WARNA BACKGROUND"
        "\nHANYA JIKA user EKPLISIT memakai kata 'warna', 'tema', 'background' (contoh: 'ubah jadi biru') → LAKUKAN:"
        "\n• bg_color: Gunakan Tailwind class yang diawali 'bg-' (contoh: 'bg-blue-900')"
        "\n• text_color: Jika background gelap set 'text-slate-100', terang 'text-slate-900'"
        "\nJIKA TIDAK DIMINTA UBAH WARNA → bg_color: null, text_color: null. INI WAJIB!"

        "\n\n📋 FITUR 2: UBAH POSISI KPI"
        "\nJIKA user minta tukar posisi KPI → kpi_positions: Array berisi urutan baru."
        "\nWAJIB Gunakan ID ini: 'kpi-total-film', 'kpi-avg-price', 'kpi-total-genre'."
        "\nContoh: [{\"id\": \"kpi-total-film\", \"order\": 3}, {\"id\": \"kpi-avg-price\", \"order\": 1}, {\"id\": \"kpi-total-genre\", \"order\": 2}]"
        "\nJika tidak diminta → kpi_positions: null"

        "\n\n📋 FITUR 3: ANALISIS DIAGRAM"
        "\nJawab pertanyaan tren/durasi menggunakan data FAKTA DATABASE."

        "\n\n📋 FITUR 4: FILTER TABEL FILM"
        "\nJIKA user minta filter horor/drama dll → table_filter: keyword. Jika tidak → table_filter: null"

        "\n\n📋 FITUR 5: UBAH POSISI DIAGRAM"
        "\nJIKA user minta pindah diagram ke atas/bawah → diagram_position: 'atas'/'bawah'. Jika tidak → null"

        "\n\n📋 FITUR 6: UBAH TIPE DIAGRAM"
        "\nJIKA user minta: 'ganti jadi diagram pie', 'ubah ke bar chart', 'bentuk garis' → LAKUKAN:"
        "\n• diagram_type: String 'bar', 'pie', atau 'line'."
        "\nJika TIDAK diminta → diagram_type: null"

        "\n\n--- FORMAT RESPONS WAJIB (VALID JSON) ---"
        "\n{"
        "\n  \"layout\": {"
        "\n    \"bg_color\": null atau string Tailwind,"
        "\n    \"text_color\": null atau string Tailwind,"
        "\n    \"kpi_positions\": null atau array,"
        "\n    \"table_filter\": null atau string,"
        "\n    \"diagram_position\": null atau 'atas'/'bawah',"
        "\n    \"diagram_type\": null atau 'bar'/'pie'/'line'"
        "\n  },"
        "\n  \"message\": \"Respons naturalmu di sini.\""
        "\n}"
    )
    messages = [{"role": "system", "content": system_instruction}]
    messages.extend(chat_history[-4:]) 
    messages.append({"role": "user", "content": request.prompt})

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={"model": "llama-3.1-8b-instant", "messages": messages, "response_format": {"type": "json_object"}, "temperature": 0.3}
            )
            
            res_data = response.json()
            
            if 'choices' not in res_data:
                error_detail = res_data.get('error', {}).get('message', str(res_data))
                return {"layout": None, "message": f"🔴 Groq API Menolak: {error_detail}"}
            
            raw_content = res_data['choices'][0]['message']['content']
            
            try: 
                ai_response = json.loads(raw_content)
                if 'message' not in ai_response:
                    ai_response['message'] = "Perintah UI diproses."
            except json.JSONDecodeError: 
                ai_response = {"layout": None, "message": raw_content}
            
            final_layout = ai_response.get('layout', ai_response) 
            final_message = ai_response.get('message')
            
            chat_history.append({"role": "user", "content": request.prompt})
            chat_history.append({"role": "assistant", "content": final_message})
            
            return {"layout": final_layout, "message": final_message}
            
    except Exception as e:
        traceback.print_exc()
        return {"message": f"🔴 Backend Error: {str(e)}", "layout": None}