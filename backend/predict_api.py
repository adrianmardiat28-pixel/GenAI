# backend/predict_api.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import json
import os
from database import fetch_data

router = APIRouter()

# --- 1. MEMUAT MODEL DENGAN PATH HANDLING ---
model_file = os.path.join(os.path.dirname(__file__), 'movie_demand_bundle.pkl')
print(f"[DEBUG] Looking for model at: {model_file}")
print(f"[DEBUG] File exists: {os.path.exists(model_file)}")

try:
    bundle = joblib.load(model_file)
    model = bundle['model']
    features = bundle['features']
    print(f"[OK] ✅ ML Model Loaded Successfully from {model_file}")
    print(f"[OK] Features: {features}")
except FileNotFoundError:
    print(f"[ERROR] ❌ Model file tidak ditemukan di: {model_file}")
    model = None
    features = None
except Exception as e:
    print(f"[ERROR] ❌ Gagal memuat model: {e}")
    import traceback
    traceback.print_exc()
    model = None
    features = None

# Struktur Input dari HTML
class PredictRequest(BaseModel):
    genre: str
    rating: str
    rental_duration: int
    rental_rate: float
    length: int
    replacement_cost: float

# --- 2. ENDPOINT PREDIKSI AI ---
@router.post("/api/predict_advanced")
def predict_advanced(data: PredictRequest):
    if model is None or features is None:
        print("[ERROR] Model tidak siap saat endpoint /api/predict_advanced dipanggil!")
        raise HTTPException(
            status_code=500, 
            detail="❌ Model Machine Learning belum tersedia. Silakan jalankan 'python train_model.py' di backend terlebih dahulu untuk melatih model."
        )

    try:
        print(f"[INFO] Predicting untuk: genre={data.genre}, rating={data.rating}")
        
        # Menyamakan format input dengan 'features' dari bundle
        input_df = pd.DataFrame(0, index=[0], columns=features)
        
        input_df['rental_duration'] = data.rental_duration
        input_df['rental_rate'] = data.rental_rate
        input_df['length'] = data.length
        input_df['replacement_cost'] = data.replacement_cost
        
        genre_col = f"genre_{data.genre}"
        rating_col = f"rating_{data.rating}"
        
        if genre_col in input_df.columns: 
            input_df[genre_col] = 1
            print(f"[INFO] Set {genre_col} = 1")
        else:
            print(f"[WARN] Genre column {genre_col} tidak ditemukan di features")
            
        if rating_col in input_df.columns: 
            input_df[rating_col] = 1
            print(f"[INFO] Set {rating_col} = 1")
        else:
            print(f"[WARN] Rating column {rating_col} tidak ditemukan di features")

        print(f"[DEBUG] Input shape: {input_df.shape}")
        print(f"[DEBUG] Input:\n{input_df}")

        # Hasil AI
        prediction_array = model.predict(input_df)
        probabilities_array = model.predict_proba(input_df)
        
        print(f"[DEBUG] Prediction array: {prediction_array}")
        print(f"[DEBUG] Probabilities array: {probabilities_array}")
        
        prediction = int(prediction_array[0])
        probabilities = probabilities_array[0]
        
        # Validate values
        if pd.isna(probabilities).any():
            print(f"[ERROR] NaN detected in probabilities: {probabilities}")
            raise ValueError("Model prediction returned NaN values")
        
        confidence = float(probabilities[prediction])
        prob_sepi = float(probabilities[0])
        prob_laris = float(probabilities[1])
        
        print(f"[DEBUG] Confidence: {confidence}, Sepi: {prob_sepi}, Laris: {prob_laris}")

        result = {
            "prediction": prediction,
            "confidence": confidence,
            "prob_laris": prob_laris,
            "prob_sepi": prob_sepi
        }
        
        print(f"[OK] Prediction result: {result}")
        return result
        
    except Exception as e:
        print(f"[ERROR] Exception di predict_advanced: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Prediction Error: {str(e)}")

# --- 3. ENDPOINT STATISTIK (HISTORIS) ---
@router.get("/api/predict_stats")
def get_predict_stats():
    try:
        # A. Query Distribusi Rating
        q_rating = "SELECT rating, COUNT(*) as jumlah FROM film GROUP BY rating ORDER BY jumlah DESC;"
        df_rating = fetch_data(q_rating)

        # B. Query Ranking Winners vs Losers (SAMA PERSIS DENGAN STREAMLIT)
        q_rank = """
            SELECT 
                c.name AS genre, 
                COUNT(r.rental_id) AS total_sewa
            FROM category c
            JOIN film_category fc ON c.category_id = fc.category_id
            JOIN film f ON fc.film_id = f.film_id
            JOIN inventory i ON f.film_id = i.film_id
            JOIN rental r ON i.inventory_id = r.rental_id
            GROUP BY c.name
            ORDER BY total_sewa DESC;
        """
        df_rank = fetch_data(q_rank)

        # Konversi ke JSON aman untuk dikirim ke HTML
        return {
            "rating_dist": json.loads(df_rating.to_json(orient="records")),
            "winners": json.loads(df_rank.head(3).to_json(orient="records")),
            "losers": json.loads(df_rank.tail(3).sort_values('total_sewa', ascending=True).to_json(orient="records"))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))