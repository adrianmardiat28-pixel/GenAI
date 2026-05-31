import json
import httpx
import traceback
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict
from analysis_api import get_full_analysis

router = APIRouter()

GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Global chat history untuk mempertahankan konteks percakapan
chat_history: List[Dict[str, str]] = []

class AnalysisChatRequest(BaseModel):
    prompt: str
    dashboard_context: str

@router.post("/chat-analysis")
async def chat_analysis(request: AnalysisChatRequest):
    global chat_history
    
    try:
        # Mengambil data terbaru dari database melalui analysis_api.py
        db_data = get_full_analysis()
        
        # System Instruction harus berada di dalam fungsi agar bisa mengakses db_data
        system_instruction = (
            "Kamu adalah Senior Data Scientist khusus untuk 'Store Analysis Dashboard'.\n\n"
            f"--- DATA REAL-TIME DATABASE ---\n{json.dumps(db_data)}\n\n"
            
            "🚨 ATURAN OUTPUT JSON 🚨\n"
            "1. DIAGRAM_TYPE: Jika user minta ubah grafik, isi 'bar', 'line', atau 'donut'.\n"
            "2. TARGET_CHART: WAJIB DIISI jika mengubah diagram. Pilih salah satu: 'genre', 'rating', 'film', atau 'trend'.\n"
            "   Contoh: Jika user minta ubah grafik genre, kirim: {\"diagram_type\": \"donut\", \"target_chart\": \"genre\"}\n"
            "3. BG_COLOR: Gunakan Tailwind (misal 'bg-slate-900'). Jika tidak diminta, biarkan null.\n\n"
            
            "🚨 TUGAS ANALISIS 🚨\n"
            "Jawablah dengan analisis mendalam (kenapa Store 1 vs Store 2 berbeda) berdasarkan data trend dan genre.\n"
            "Berikan insight strategis, bukan hanya membaca angka.\n\n"
            
            "--- FORMAT RESPONS WAJIB (VALID JSON) ---\n"
            "{\"layout\": {\"bg_color\": null, \"store_position\": null, \"diagram_type\": null, \"target_chart\": null}, \"message\": \"Analisis mendalam kamu\"}"
        )

        # Menggabungkan instruksi sistem, riwayat chat, dan pesan terbaru user
        messages = [{"role": "system", "content": system_instruction}] 
        messages.extend(chat_history[-4:]) 
        messages.append({"role": "user", "content": request.prompt})
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                GROQ_URL, 
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={
                    "model": "llama-3.1-8b-instant", 
                    "messages": messages, 
                    "response_format": {"type": "json_object"}, 
                    "temperature": 0.1 # Suhu rendah agar AI tetap faktual berbasis data
                }
            )
            
            res_data = response.json()
            
            # Validasi respons dari Groq API
            if 'choices' not in res_data:
                error_msg = res_data.get('error', {}).get('message', 'API Groq sedang sibuk.')
                return {"layout": None, "message": f"🔴 Kendala AI: {error_msg}"}
                
            # Parsing konten JSON dari AI
            raw_content = res_data['choices'][0]['message']['content']
            ai_content = json.loads(raw_content)
            
            # Update riwayat percakapan
            chat_history.append({"role": "user", "content": request.prompt})
            chat_history.append({"role": "assistant", "content": ai_content.get('message')})
            
            return ai_content
            
    except Exception as e:
        # Menampilkan error di terminal VS Code untuk debugging
        traceback.print_exc()
        return {"message": f"🔴 Backend Error: {str(e)}", "layout": None}