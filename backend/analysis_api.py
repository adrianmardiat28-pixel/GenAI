# backend/analysis_api.py
from fastapi import APIRouter, HTTPException
from database import fetch_data
import pandas as pd
import json

router = APIRouter()

SUMMARY_QUERY = """
WITH genre_base AS (
    SELECT i.store_id, c.name AS genre, COUNT(*) AS total_rental
    FROM rental r
    JOIN inventory i ON r.inventory_id = i.inventory_id
    JOIN film f ON i.film_id = f.film_id
    JOIN film_category fc ON f.film_id = fc.film_id
    JOIN category c ON fc.category_id = c.category_id
    GROUP BY i.store_id, c.name
),
genre_ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY store_id ORDER BY total_rental DESC, genre) AS rn
    FROM genre_base
),
rating_base AS (
    SELECT i.store_id, f.rating, COUNT(*) AS total_rental
    FROM rental r
    JOIN inventory i ON r.inventory_id = i.inventory_id
    JOIN film f ON i.film_id = f.film_id
    GROUP BY i.store_id, f.rating
),
rating_ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY store_id ORDER BY total_rental DESC, rating) AS rn
    FROM rating_base
),
film_base AS (
    SELECT i.store_id, f.title, COUNT(*) AS total_rental
    FROM rental r
    JOIN inventory i ON r.inventory_id = i.inventory_id
    JOIN film f ON i.film_id = f.film_id
    GROUP BY i.store_id, f.title
),
film_ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY store_id ORDER BY total_rental DESC, title) AS rn
    FROM film_base
)
SELECT s.store_id, gr.genre AS dominant_genre, rr.rating AS dominant_rating, 
       fr.title AS top_film, fr.total_rental AS top_film_total_rental
FROM store s
LEFT JOIN genre_ranked gr ON s.store_id = gr.store_id AND gr.rn = 1
LEFT JOIN rating_ranked rr ON s.store_id = rr.store_id AND rr.rn = 1
LEFT JOIN film_ranked fr  ON s.store_id = fr.store_id AND fr.rn = 1
ORDER BY s.store_id;
"""

def top_genre_query(store_id):
    return f"""
    SELECT c.name AS genre, COUNT(*) AS total_rental
    FROM rental r JOIN inventory i ON r.inventory_id = i.inventory_id
    JOIN film f ON i.film_id = f.film_id JOIN film_category fc ON f.film_id = fc.film_id
    JOIN category c ON fc.category_id = c.category_id
    WHERE i.store_id = {store_id} GROUP BY c.name ORDER BY total_rental DESC, genre LIMIT 10;
    """

def top_rating_query(store_id):
    return f"""
    SELECT f.rating, COUNT(*) AS total_rental
    FROM rental r JOIN inventory i ON r.inventory_id = i.inventory_id
    JOIN film f ON i.film_id = f.film_id
    WHERE i.store_id = {store_id} GROUP BY f.rating ORDER BY total_rental DESC, f.rating;
    """

def top_film_query(store_id):
    return f"""
    SELECT f.title, COUNT(*) AS total_rental
    FROM rental r JOIN inventory i ON r.inventory_id = i.inventory_id
    JOIN film f ON i.film_id = f.film_id
    WHERE i.store_id = {store_id} GROUP BY f.title ORDER BY total_rental DESC, f.title LIMIT 10;
    """

def trend_query(store_id):
    return f"""
    WITH monthly_rental AS (
        SELECT DATE_TRUNC('month', r.rental_date) AS month_date, COUNT(*) AS total_rental
        FROM rental r JOIN inventory i ON r.inventory_id = i.inventory_id
        WHERE i.store_id = {store_id} GROUP BY DATE_TRUNC('month', r.rental_date)
    ),
    monthly_trend AS (
        SELECT month_date, total_rental, LAG(total_rental) OVER (ORDER BY month_date) AS prev_month
        FROM monthly_rental
    )
    SELECT TO_CHAR(month_date, 'YYYY-MM') AS month, total_rental, prev_month,
        CASE WHEN prev_month IS NULL THEN 'awal data' WHEN total_rental > prev_month THEN 'naik'
             WHEN total_rental < prev_month THEN 'turun' ELSE 'tetap' END AS trend
    FROM monthly_trend ORDER BY month;
    """

def safe_to_dict(df):
    if df is not None and not df.empty:
        json_str = df.to_json(orient="records")
        return json.loads(json_str)
    return []

@router.get("/api/analysis")
def get_full_analysis():
    try:
        summary_df = fetch_data(SUMMARY_QUERY)
        payload = {
            "summary": safe_to_dict(summary_df),
            "store1": {},
            "store2": {}
        }
        
        for store_id in [1, 2]:
            store_key = f"store{store_id}"
            payload[store_key]["genre"] = safe_to_dict(fetch_data(top_genre_query(store_id)))
            payload[store_key]["rating"] = safe_to_dict(fetch_data(top_rating_query(store_id)))
            payload[store_key]["film"] = safe_to_dict(fetch_data(top_film_query(store_id)))
            payload[store_key]["trend"] = safe_to_dict(fetch_data(trend_query(store_id)))
            
        return payload

    except Exception as e:
        print(f"❌ Error API Analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))