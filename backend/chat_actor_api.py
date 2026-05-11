# backend/chat_actor_api.py
import json, httpx, traceback
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List
from database import fetch_data

router = APIRouter()
GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Global chat history untuk memori percakapan
chat_history: List[Dict[str, str]] = []

def get_actor_db_summary():
    """Ambil ringkasan data aktor dari database untuk memperkuat context AI."""
    summary = ""
    try:
        # Total aktor
        df = fetch_data("SELECT COUNT(DISTINCT actor_id) as total FROM actor;")
        if df is not None and not df.empty:
            summary += f"\n- Total Aktor Terdaftar: {int(df['total'].iloc[0])}"

        # Rata-rata film per aktor
        df_avg = fetch_data("""
            SELECT AVG(film_count) as avg_films FROM (
                SELECT actor_id, COUNT(*) as film_count FROM film_actor GROUP BY actor_id
            ) sub;
        """)
        if df_avg is not None and not df_avg.empty:
            summary += f"\n- Rata-rata Produktivitas: {float(df_avg['avg_films'].iloc[0]):.1f} film per aktor"

    except Exception as e:
        summary += f"\n- DB Error: {e}"
    return summary

class ActorChatRequest(BaseModel):
    prompt: str
    page_context: Dict

@router.post("/chat-actor")
async def chat_actor(request: ActorChatRequest):
    global chat_history
    try:
        ctx = request.page_context

        # === BUILD SYSTEM PROMPT (UI CONTROL + STAR POWER ANALYSIS) ===
        system_instruction = (
            "Kamu adalah 'Actor AI', Senior Industry Analyst untuk Dashboard Adrian.\n\n"
            f"--- DATA VISUAL SAAT INI (SCRAPED) ---\n{json.dumps(ctx)}\n"
            f"--- DATA DATABASE ---\n{get_actor_db_summary()}\n\n"

            "🚨 ATURAN KONTROL UI (WAJIB JSON) 🚨\n"
            "1. BG_COLOR: Jika user minta ganti warna/tema, gunakan Tailwind (misal: 'bg-slate-900', 'bg-white'). Jika tidak, null.\n"
            "2. DIAGRAM_TYPE: Jika user minta ubah bentuk grafik, isi dengan 'bar', 'line', 'scatter', 'donut', atau 'pie'. Jika tidak, null.\n"
            "3. TARGET_CHART: WAJIB diisi jika DIAGRAM_TYPE ada. Pilih: 'actor' (untuk Top 10) atau 'film' (untuk detail film).\n\n"

            "🚨 TUGAS DEEP ANALYSIS 🚨\n"
            "- Analisis 'Star Power': Bandingkan apakah revenue tinggi karena jumlah film banyak (produktivitas) atau karena kualitas film (revenue per film tinggi).\n"
            "- Jika user bertanya tentang aktor tertentu, gunakan data dari 'actor_chart' dan 'film_chart'.\n"
            "- Berikan saran strategi: aktor mana yang paling layak diberikan kontrak film blockbuster berikutnya.\n\n"

            "--- FORMAT OUTPUT WAJIB (JSON) ---\n"
            "{\"layout\": {\"bg_color\": null, \"diagram_type\": null, \"target_chart\": null}, \"message\": \"Analisis mendalam kamu\"}"
        )

        messages = [{"role": "system", "content": system_instruction}] + chat_history[-4:] + [{"role": "user", "content": request.prompt}]

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                GROQ_URL, 
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": messages,
                    "response_format": {"type": "json_object"},
                    "temperature": 0.2
                }
            )
            
            res_data = response.json()
            if 'choices' not in res_data:
                return {"message": "⚠️ API sedang sibuk.", "layout": None}
                
            raw_content = res_data['choices'][0]['message']['content']
            ai_content = json.loads(raw_content)
            
            # Simpan history
            chat_history.append({"role": "user", "content": request.prompt})
            chat_history.append({"role": "assistant", "content": ai_content.get('message', '')})
            
            # --- PENTING: RETURN KEDUA FIELD UNTUK DISINKRONKAN DENGAN actor_ai.js ---
            return {
                "message": ai_content.get('message'),
                "layout": ai_content.get('layout')
            }
            
    except Exception as e:
        traceback.print_exc()
        return {"message": f"🔴 Backend Error: {str(e)}", "layout": None}