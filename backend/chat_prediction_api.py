# backend/chat_prediction_api.py
import json, httpx, traceback
from fastapi import APIRouter
from pydantic import BaseModel  # pyrefly: ignore [missing-import]
from typing import List, Dict
from predict_api import get_predict_stats  # pyrefly: ignore [missing-import]

router = APIRouter()
GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
chat_history = []

class PredictionChatRequest(BaseModel):
    prompt: str
    page_context: Dict

@router.post("/chat-prediction")
async def chat_prediction(request: PredictionChatRequest):
    global chat_history
    try:
        # Ambil data statistik mentah yang juga dipakai diagram di layar
        db_stats = get_predict_stats()
        ctx = request.page_context

        # Ekstrak semua konteks dari frontend
        inputs = ctx.get('inputs', {})
        ml_result = ctx.get('ml_result', {})
        analisis_model = ctx.get('analisis_model', {})
        chart_data = ctx.get('data_chart_di_layar', {})
        rekomendasi_historis = ctx.get('rekomendasi_manajerial_historis', '')

        system_instruction = (
            "Kamu adalah 'Predict AI Master', Senior Data Scientist & Konsultan Bisnis Perfilman yang SANGAT KRITIS dan CERDAS. "
            "Kamu bisa MEMBACA dan MENGANALISIS semua data di halaman Prediction, termasuk semua chart/diagram yang tampil di layar user."
            
            "\n\n==============================="
            "\n📋 BAGIAN 1: INPUT FILM DARI USER"
            "\n==============================="
            f"\n- Genre: {inputs.get('genre', 'Belum dipilih')}"
            f"\n- Rating Usia: {inputs.get('rating', 'Belum dipilih')}"
            f"\n- Harga Sewa: ${inputs.get('rental_rate_usd', '?')}"
            f"\n- Durasi Sewa: {inputs.get('rental_duration_days', '?')} hari"
            f"\n- Durasi Film: {inputs.get('film_length_minutes', '?')} menit"
            f"\n- Biaya Penggantian: ${inputs.get('replacement_cost_usd', '?')}"
            
            "\n\n==============================="
            "\n🤖 BAGIAN 2: HASIL PREDIKSI MODEL ML"
            "\n==============================="
            f"\n- Label Prediksi: {ml_result.get('status', 'Belum ada')}"
            f"\n- Confidence Score: {ml_result.get('confidence', '0%')}"
            f"\n- Sudah diprediksi: {ml_result.get('sudah_diprediksi', False)}"
            
            "\n\n==============================="
            "\n📊 BAGIAN 3: ANALISIS YANG TAMPIL DI LAYAR"
            "\n==============================="
            f"\n- Mengapa Demikian (Interpretasi Model): {analisis_model.get('mengapa_demikian', 'Belum ada')}"
            f"\n- Rekomendasi Strategis: {analisis_model.get('rekomendasi_strategis', 'Belum ada')}"
            
            "\n\n==============================="
            "\n📈 BAGIAN 4: DATA CHART/DIAGRAM DI LAYAR"
            "\n==============================="
        )

        # Tambahkan data chart secara detail
        if chart_data.get('rating_distribution'):
            system_instruction += "\n\n🔵 CHART 1 - Distribusi Film Berdasarkan Rating (Bar Chart Biru):"
            for item in chart_data['rating_distribution']:
                system_instruction += f"\n  • Rating {item.get('rating')}: {item.get('jumlah_film')} film"

        if chart_data.get('top_genre_laris'):
            system_instruction += "\n\n🟢 CHART 2 - Top 3 Genre Laris / Winners (Bar Chart Hijau, > 16 sewa):"
            for item in chart_data['top_genre_laris']:
                system_instruction += f"\n  • {item.get('genre')}: {item.get('total_sewa')} total sewa"

        if chart_data.get('top_genre_sepi'):
            system_instruction += "\n\n🔴 CHART 3 - Top 3 Genre Sepi / Losers (Bar Chart Merah, < 16 sewa):"
            for item in chart_data['top_genre_sepi']:
                system_instruction += f"\n  • {item.get('genre')}: {item.get('total_sewa')} total sewa"

        if chart_data.get('donut_probabilitas'):
            donut = chart_data['donut_probabilitas']
            system_instruction += "\n\n🍩 CHART 4 - Donut Chart Probabilitas Prediksi:"
            if donut.get('labels') and donut.get('values'):
                for i, label in enumerate(donut['labels']):
                    val = donut['values'][i] if i < len(donut['values']) else '?'
                    if isinstance(val, (int, float)):
                        system_instruction += f"\n  • {label}: {val*100:.1f}%"
                    else:
                        system_instruction += f"\n  • {label}: {val}"

        if rekomendasi_historis:
            system_instruction += f"\n\n💡 REKOMENDASI MANAJERIAL HISTORIS (tampil di bawah chart):\n{rekomendasi_historis}"

        # Tambahkan data mentah dari database sebagai cross-reference
        system_instruction += (
            "\n\n==============================="
            "\n🗄️ BAGIAN 5: DATA MENTAH DATABASE (cross-reference)"
            "\n==============================="
            f"\n{json.dumps(db_stats, indent=2)}"
        )

        # Protokol analisis yang lebih kuat
        system_instruction += (
            "\n\n==============================="
            "\n🚨 PROTOKOL ANALISIS KRITIS 🚨"
            "\n==============================="
            "\n1. BACA CHART: Kamu BISA dan HARUS membaca semua data chart di atas. Jika user bertanya 'apa yang ada di chart?', 'jelaskan diagram', 'baca grafik', JAWAB dengan data spesifik dari BAGIAN 4."
            "\n2. ANALISIS PREDIKSI: Jika user bertanya 'kenapa prediksi ini?', jelaskan berdasarkan BAGIAN 2 (hasil ML) dan BAGIAN 3 (interpretasi model). Hubungkan dengan data chart untuk memberikan penjelasan yang data-driven."
            "\n3. CROSS-REFERENCE: Bandingkan genre yang dipilih user dengan data Winners/Losers di chart. Apakah genre-nya termasuk yang laris atau sepi? Berikan insight berdasarkan data historis."
            "\n4. JELASKAN 'WHY': Selalu jelaskan MENGAPA. Misalnya: 'Genre Horror hanya punya 846 total sewa (lihat chart Losers), sementara Sports punya 1.081 sewa. Ini menunjukkan bahwa genre pilihan Anda kurang diminati secara historis.'"
            "\n5. LOGIKA ANTI-HALUSINASI: 'rental_duration' = HARI sewa. 'length' = MENIT film. Jangan campur adukkan!"
            "\n6. SOLUSI SPESIFIK: Berikan angka spesifik. Contoh: 'Turunkan harga ke $2.99 berdasarkan rata-rata genre ini di database.'"

            "\n8. JIKA BELUM DIPREDIKSI: Jika 'sudah_diprediksi' = false, sarankan user untuk mengisi form dan klik 'Analisis Permintaan Pasar' dulu."
            "\n9. BAHASA: Jawab dalam bahasa yang sama dengan user (Indonesia/Inggris)."
            
            "\n\n--- FORMAT JSON WAJIB ---"
            "\n{\"message\": \"Tulis analisis mendalam, kritis, dan data-driven di sini. Gunakan emoji dan bold (**text**) untuk emphasis.\"}"
        )

        messages = [{"role": "system", "content": system_instruction}] + chat_history[-6:] + [{"role": "user", "content": request.prompt}]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(GROQ_URL, headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={"model": "llama-3.1-8b-instant", "messages": messages, "response_format": {"type": "json_object"}, "temperature": 0.3})
            
            res_data = response.json()
            print("Groq raw response status:", response.status_code)
            
            # Handle API errors (rate limit, token limit, invalid key, etc.)
            if response.status_code != 200 or 'error' in res_data:
                error_msg = res_data.get('error', {}).get('message', f'HTTP {response.status_code}')
                print(f"Groq API Error: {error_msg}")
                return {"message": f"⚠️ AI sedang sibuk atau prompt terlalu panjang. Coba lagi dalam beberapa detik.\n\nDetail: {error_msg}"}
            
            if 'choices' not in res_data or len(res_data['choices']) == 0:
                print("Groq response tanpa choices:", res_data)
                return {"message": "⚠️ AI tidak memberikan respons. Silakan coba lagi."}

            ai_content = json.loads(res_data['choices'][0]['message']['content'])
            
            chat_history.append({"role": "user", "content": request.prompt})
            chat_history.append({"role": "assistant", "content": ai_content.get('message')})
            return ai_content
            
    except Exception as e:
        traceback.print_exc()
        return {"message": f"🔴 Backend Error: {str(e)}", "layout": None}