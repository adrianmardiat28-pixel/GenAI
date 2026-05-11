# backend/revenue_api.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from database import fetch_data
import json
import httpx
import pickle
import pandas as pd
from datetime import timedelta
import re

router = APIRouter()

# ==========================================
# ENDPOINT DATA STANDAR (TIDAK DIUBAH)
# ==========================================

# 1. API Pendapatan Harian (Daily Revenue)
@router.get("/api/revenue/daily")
def get_daily_revenue():
    query = """
        SELECT DATE(payment_date) as date, SUM(amount) as daily_revenue
        FROM payment
        GROUP BY DATE(payment_date)
        ORDER BY date;
    """
    df = fetch_data(query)
    if df is None:
        raise HTTPException(status_code=500, detail="Gagal mengambil data pendapatan harian")
    return json.loads(df.to_json(orient="records"))

# 2. API Top 10 Film (Movie Revenue)
@router.get("/api/revenue/movies")
def get_movie_revenue():
    query = """
        SELECT f.title as movie_title, SUM(p.amount) as total_revenue
        FROM payment p
        JOIN rental r ON p.rental_id = r.rental_id
        JOIN inventory i ON r.inventory_id = i.inventory_id
        JOIN film f ON i.film_id = f.film_id
        GROUP BY f.title
        ORDER BY total_revenue DESC
        LIMIT 10; 
    """
    df = fetch_data(query)
    if df is None:
        raise HTTPException(status_code=500, detail="Gagal mengambil data pendapatan film")
    return json.loads(df.to_json(orient="records"))

# 3. API Pendapatan Per Genre (Genre Revenue)
@router.get("/api/revenue/genres")
def get_genre_revenue():
    query = """
        SELECT c.name as genre, SUM(p.amount) as total_revenue
        FROM payment p
        JOIN rental r ON p.rental_id = r.rental_id
        JOIN inventory i ON r.inventory_id = i.inventory_id
        JOIN film_category fc ON i.film_id = fc.film_id
        JOIN category c ON fc.category_id = c.category_id
        GROUP BY c.name
        ORDER BY total_revenue DESC;
    """
    df = fetch_data(query)
    if df is None:
        raise HTTPException(status_code=500, detail="Gagal mengambil data pendapatan genre")
    return json.loads(df.to_json(orient="records"))


# ==========================================
# ENDPOINT AI & MACHINE LEARNING (BARU)
# ==========================================

GROQ_API_KEY = "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"
GROQ_URL = "[https://api.groq.com/openai/v1/chat/completions](https://api.groq.com/openai/v1/chat/completions)"

class RevenueChatRequest(BaseModel):
    prompt: str
    page_context: Optional[Dict[str, Any]] = None

@router.post("/chat-revenue")
async def chat_revenue(request: RevenueChatRequest):
    prompt_lower = request.prompt.lower()
    
    # Kumpulan kata kunci agar typo seperti "predic" tetap terbaca
    trigger_words = ["prediksi", "predic", "ramal", "future", "forecast"]
    
    # ==========================================
    # LOGIKA 1: PREDIKSI TIME SERIES & ANALISA
    # ==========================================
    if any(word in prompt_lower for word in trigger_words):
        try:
            months_to_predict = 3 
            match = re.search(r'(\d+)\s*bulan', prompt_lower)
            if match:
                months_to_predict = int(match.group(1))
            
            days_to_predict = months_to_predict * 30 

            with open('revenue_model.pkl', 'rb') as f:
                model_data = pickle.load(f)
            
            ml_model = model_data['model']
            min_date = pd.to_datetime(model_data['min_date'])
            last_date = pd.to_datetime(model_data['max_date']) 

            future_dates_str = []
            future_days_index = []
            
            for i in range(1, days_to_predict + 1):
                target_date = last_date + timedelta(days=i)
                target_index = (target_date - min_date).days
                future_dates_str.append(target_date.strftime("%Y-%m-%d"))
                future_days_index.append(target_index)
            
            X_future = pd.DataFrame({'day_index': future_days_index})
            future_preds = ml_model.predict(X_future)
            
            # Ekstrak nilai prediksi agar tidak minus
            future_values = [max(0, round(val, 2)) for val in future_preds.tolist()]
            
            # ----------------------------------------------------
            # FITUR BARU: AI MEMBUAT ANALISA HASIL PREDIKSI OTOMATIS
            # ----------------------------------------------------
            start_val = future_values[0]
            end_val = future_values[-1]
            
            if end_val > start_val:
                trend = "NAIK 📈"
            elif end_val < start_val:
                trend = "TURUN 📉"
            else:
                trend = "STABIL ➖"

            analysis_msg = (
                f"✅ **Analisa Prediksi {months_to_predict} Bulan Selesai!**\n\n"
                f"Berdasarkan perhitungan model *Linear Regression*, proyeksi pendapatan rental DVD kita menunjukkan tren **{trend}**.\n"
                f"- Estimasi awal prediksi: **${start_val:,.2f}**\n"
                f"- Estimasi akhir bulan ke-{months_to_predict}: **${end_val:,.2f}**\n\n"
                f"Silakan cek garis putus-putus oranye pada grafik untuk melihat detail pergerakan hariannya!"
            )
            
            layout_response = {
                "bg_color": None, "target_chart": None, "diagram_type": None,
                "prediction": {
                    "months": months_to_predict,
                    "future_dates": future_dates_str,
                    "future_values": future_values
                }
            }
            
            return {
                "message": analysis_msg,
                "layout": layout_response
            }
            
        except FileNotFoundError:
            return {"message": "⚠️ File `revenue_model.pkl` tidak ditemukan.", "layout": None}
        except Exception as e:
            return {"message": f"🔴 ML Prediction Error: {str(e)}", "layout": None}

    # ==========================================
    # LOGIKA 2: KONTROL UI DENGAN GROQ LLM
    # ==========================================
    context_str = json.dumps(request.page_context, indent=2) if request.page_context else "Tidak ada data."
    
    system_instruction = (
        "Kamu adalah 'AI Financial Forecaster'. Tugasmu merespons request user & mengatur UI.\n"
        f"DATA LAYAR:\n{context_str}\n\n"
        "ATURAN JSON WAJIB:\n"
        "{\n"
        "  \"message\": \"Jawaban analisis singkat dari kamu...\",\n"
        "  \"layout\": {\"bg_color\": null, \"target_chart\": null, \"diagram_type\": null, \"prediction\": null}\n"
        "}\n"
        "Jawab dengan ramah. Isi parameter 'layout' HANYA jika user meminta ganti tema (bg_color) atau ubah chart (target_chart & diagram_type)."
    )

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={
                    "model": "llama3-8b-8192", 
                    "messages": [{"role": "system", "content": system_instruction}, {"role": "user", "content": request.prompt}], 
                    "response_format": {"type": "json_object"}, 
                    "temperature": 0.4
                }
            )
            
            res_data = response.json()
            if response.status_code != 200:
                error_msg = res_data.get('error', {}).get('message', 'Unknown Error')
                return {"message": f"⚠️ Groq API Sedang Sibuk/Error: {error_msg}", "layout": None}
                
            raw_content = res_data['choices'][0]['message']['content']
            
            # Membersihkan format markdown bawaan LLM jika ada
            raw_content = raw_content.replace('```json', '').replace('```', '').strip()
            
            return json.loads(raw_content)
            
    except Exception as e:
        return {"message": f"🔴 Koneksi LLM Gagal: {str(e)}. Coba beberapa saat lagi.", "layout": None}