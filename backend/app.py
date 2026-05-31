# backend/app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.database import fetch_data
import json

# --- IMPORT ROUTER ---
# --- IMPORT ROUTER ---
from backend.analysis_api import router as analysis_router
from backend.predict_api import router as predict_router, model as predict_model
from backend.revenue_api import router as revenue_router
from backend.actor_api import router as actor_router
from backend.chat_dashboard_api import router as chat_dashboard_router
from backend.chat_analysis_api import router as chat_analysis_router
from backend.chat_prediction_api import router as chat_prediction_router
from backend.chat_revenue_api import router as chat_revenue_router
from backend.chat_actor_api import router as chat_actor_router
from backend.chat_ai_api import router as chat_ai_router
app = FastAPI(title="Movie Demand API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DAFTARKAN ROUTER ---

app.include_router(analysis_router) 
app.include_router(predict_router)
app.include_router(revenue_router)
app.include_router(actor_router)
app.include_router(chat_dashboard_router)
app.include_router(chat_analysis_router)
app.include_router(chat_prediction_router)
app.include_router(chat_revenue_router)
app.include_router(chat_actor_router)
app.include_router(chat_ai_router)

# =====================================================================
# HEALTH CHECK & MODEL STATUS
# =====================================================================
@app.get("/health")
def health_check():
    """Check if API and ML model are ready"""
    print(f"[HEALTH] Predict model status: {predict_model is not None}")
    return {
        "status": "ok",
        "ml_model": "ready" if predict_model else "not_ready",
        "message": "✅ API Online" if predict_model else "⚠️ ML Model tidak tersedia"
    }

# =====================================================================
# 1. ENDPOINT UNTUK DASHBOARD (MENAMPILKAN SEMUA FILM)
# Ini yang tadi sempat hilang/tertimpa (404 Not Found)
# =====================================================================
@app.get("/api/movies")
def get_movies():
    query = """
        SELECT f.film_id, f.title, f.release_year, f.rental_rate, f.length, f.rating, c.name as genre, f.description
        FROM film f
        LEFT JOIN film_category fc ON f.film_id = fc.film_id
        LEFT JOIN category c ON fc.category_id = c.category_id
        ORDER BY f.film_id ASC;
    """
    df = fetch_data(query)
    if df is None:
        raise HTTPException(status_code=500, detail="Gagal mengambil data dari database")
    
    return df.to_dict(orient="records")


# =====================================================================
# 2. ENDPOINT UNTUK HALAMAN DETAIL (MENAMPILKAN 1 FILM + AKTOR)
# =====================================================================
@app.get("/api/movies/{movie_id}")
def get_movie_detail(movie_id: int):
    # Query Detail Film
    q_detail = f"""
        SELECT f.*, l.name as lang, c.name as genre 
        FROM film f 
        JOIN language l ON f.language_id = l.language_id 
        LEFT JOIN film_category fc ON f.film_id = fc.film_id
        LEFT JOIN category c ON fc.category_id = c.category_id
        WHERE f.film_id = {movie_id}
    """
    df_detail = fetch_data(q_detail)
    
    if df_detail is None or df_detail.empty:
        raise HTTPException(status_code=404, detail="Film tidak ditemukan")
        
    # Query Daftar Pemeran (Cast)
    q_actors = f"""
        SELECT a.first_name, a.last_name 
        FROM actor a 
        JOIN film_actor fa ON a.actor_id = fa.actor_id 
        WHERE fa.film_id = {movie_id}
    """
    df_actors = fetch_data(q_actors)
    actors_list = []
    if df_actors is not None and not df_actors.empty:
        actors_list = [f"{row['first_name']} {row['last_name']}" for _, row in df_actors.iterrows()]
        
    # Gabungkan dan bersihkan data agar aman untuk JSON
    json_str = df_detail.to_json(orient="records", date_format="iso")
    movie_data = json.loads(json_str)[0]
    movie_data["cast"] = ", ".join(actors_list) # Memasukkan daftar aktor
    
    return movie_data