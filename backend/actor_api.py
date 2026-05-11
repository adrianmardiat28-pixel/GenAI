# backend/actor_api.py
from fastapi import APIRouter, HTTPException
from database import fetch_data
import json

router = APIRouter()

# 1. API Top 10 Actors by Allocated Revenue
@router.get("/api/actors/top10")
def get_top_actors():
    query = """
    WITH actor_count_per_film AS (
        SELECT film_id, COUNT(*) AS total_actors
        FROM film_actor GROUP BY film_id
    ),
    actor_revenue AS (
        SELECT
            a.actor_id,
            a.first_name || ' ' || a.last_name AS actor_name,
            COUNT(DISTINCT r.rental_id) AS total_rentals,
            SUM(p.amount / ac.total_actors) AS allocated_revenue
        FROM payment p
        JOIN rental r ON p.rental_id = r.rental_id
        JOIN inventory i ON r.inventory_id = i.inventory_id
        JOIN film_actor fa ON i.film_id = fa.film_id
        JOIN actor a ON fa.actor_id = a.actor_id
        JOIN actor_count_per_film ac ON i.film_id = ac.film_id
        GROUP BY a.actor_id, actor_name
    )
    SELECT actor_id, actor_name, total_rentals, ROUND(allocated_revenue::numeric, 2) AS total_revenue
    FROM actor_revenue ORDER BY total_revenue DESC LIMIT 10;
    """
    df = fetch_data(query)
    if df is None:
        raise HTTPException(status_code=500, detail="Gagal mengambil data aktor")
    return json.loads(df.to_json(orient="records"))

# 2. API Top Films for Specific Actor
@router.get("/api/actors/{actor_id}/films")
@router.get("/api/actors/{actor_id}/films")
def get_actor_films(actor_id: int):
    # Query ini menggunakan SUM(p.amount) secara utuh tanpa pembagian aktor
    # Menggunakan COUNT(DISTINCT r.rental_id) untuk memastikan jumlah sewa akurat
    query = f"""
    SELECT
        f.title,
        COUNT(DISTINCT r.rental_id) AS total_rentals,
        ROUND(SUM(p.amount)::numeric, 2) AS total_revenue
    FROM actor a
    JOIN film_category fc ON a.actor_id = a.actor_id -- Memastikan relasi ke film melalui category/actor
    JOIN film_actor fa ON a.actor_id = fa.actor_id
    JOIN film f ON fa.film_id = f.film_id
    JOIN inventory i ON f.film_id = i.film_id
    JOIN rental r ON i.inventory_id = r.inventory_id
    JOIN payment p ON r.rental_id = p.rental_id
    WHERE a.actor_id = {actor_id}
    GROUP BY f.title
    ORDER BY total_revenue DESC
    LIMIT 10;
    """
    df = fetch_data(query)
    
    if df is None:
        raise HTTPException(status_code=500, detail="Gagal mengambil data film")
    
    # Menghapus duplikasi jika ada baris yang tidak sengaja terhitung ganda akibat join
    return json.loads(df.to_json(orient="records"))