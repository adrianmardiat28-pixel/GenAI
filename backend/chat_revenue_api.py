# backend/chat_revenue_api.py
import json, httpx, traceback
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List
from database import fetch_data

router = APIRouter()
GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Global chat history untuk mempertahankan konteks
chat_history: List[Dict[str, str]] = []

def get_revenue_db_summary():
    """Ambil ringkasan ringkas dari database untuk memperkuat analisis AI."""
    summary = ""
    try:
        df = fetch_data("SELECT SUM(amount) as total, COUNT(*) as cnt, AVG(amount) as avg FROM payment;")
        if df is not None and not df.empty:
            summary += f"\n- Total Revenue Riil: ${float(df['total'].iloc[0]):.2f}"
            summary += f"\n- Rata-rata per Transaksi: ${float(df['avg'].iloc[0]):.2f}"

        df_m = fetch_data("""
            SELECT TO_CHAR(payment_date, 'YYYY-MM') as bulan, SUM(amount) as rev
            FROM payment GROUP BY TO_CHAR(payment_date, 'YYYY-MM') ORDER BY bulan;
        """)
        if df_m is not None and not df_m.empty:
            summary += "\n- Perbandingan Bulanan:"
            for _, row in df_m.iterrows():
                summary += f"\n  • {row['bulan']}: ${float(row['rev']):.2f}"
    except Exception as e:
        summary += f"\n- DB Error: {e}"
    return summary

class RevenueChatRequest(BaseModel):
    prompt: str
    page_context: Dict

@router.post("/chat-revenue")
async def chat_revenue(request: RevenueChatRequest):
    global chat_history
    try:
        ctx = request.page_context
        total_revenue = ctx.get('total_revenue', '$0.00')
        
        # === BUILD SYSTEM PROMPT (UI CONTROL + DEEP ANALYSIS) ===
        system_instruction = (
            "Kamu adalah 'Revenue AI', Senior Financial Analyst Dashboard milik Adrian Alrizqullah Mardiat.\n\n"
            f"--- DATA VISUAL SAAT INI ---\n{json.dumps(ctx)}\n"
            f"--- DATA DATABASE ---\n{get_revenue_db_summary()}\n\n"
            
            "🚨 TUGAS DEEP ANALYSIS 🚨\n"
            "1. Hubungkan antar data: Jika pendapatan turun, cek apakah ada genre tertentu yang performanya drop.\n"
            "2. Berikan insight finansial yang tajam, bukan sekadar membaca angka.\n"
            "3. Jika user bertanya 'kenapa', berikan argumen logis berdasarkan perbandingan genre dan trend harian.\n\n"

            "🚨 ATURAN KONTROL UI (WAJIB JSON) 🚨\n"
            "1. BG_COLOR: Jika user minta ganti warna/tema, isi dengan Tailwind (misal: 'bg-slate-900', 'bg-white'). Jika tidak, null.\n"
            "2. DIAGRAM_TYPE: Jika user minta ubah bentuk grafik, isi dengan 'bar', 'line', 'scatter', 'donut', atau 'pie'. Jika tidak, null.\n"
            "3. TARGET_CHART: WAJIB diisi jika DIAGRAM_TYPE ada. Pilih: 'daily', 'movie', atau 'genre'.\n\n"

            "--- FORMAT OUTPUT WAJIB (JSON) ---\n"
            "{\"layout\": {\"bg_color\": null, \"diagram_type\": null, \"target_chart\": null}, \"message\": \"Analisis mendalam kamu\"}"
        )

        messages = [{"role": "system", "content": system_instruction}] + chat_history[-4:] + [{"role": "user", "content": request.prompt}]

        async with httpx.AsyncClient(timeout=30.0) as client:
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
                return {"message": "⚠️ Groq AI sedang sibuk.", "layout": None}
                
            raw_content = res_data['choices'][0]['message']['content']
            ai_content = json.loads(raw_content)
            
            # Update history untuk memori percakapan
            chat_history.append({"role": "user", "content": request.prompt})
            chat_history.append({"role": "assistant", "content": ai_content.get('message', '')})
            
            # --- PENTING: RETURN KEDUA FIELD (MESSAGE & LAYOUT) ---
            return {
                "message": ai_content.get('message'),
                "layout": ai_content.get('layout')
            }
            
    except Exception as e:
        traceback.print_exc()
        return {"message": f"🔴 Backend Error: {str(e)}", "layout": None}