# backend/etl.py
import pandas as pd
from sqlalchemy import text
import sys
import os
from database import get_engine

def run_etl():
    print("--- 📥 Memulai Proses ETL dari Tabel OLAP ---")
    engine = get_engine()
    
    query = """
        SELECT 
            category_name, rental_duration, 
            rental_rate, length, replacement_cost, rating,
            is_popular 
        FROM fact_movie_demand
    """
    
    try:
        df = pd.read_sql(text(query), engine)
        
        if df.empty:
            print("❌ Error: Tabel fact_movie_demand kosong!")
            return None

        # Transformasi: Mengisi data kosong
        df['category_name'] = df['category_name'].fillna('Unknown')
        df['is_popular'] = df['is_popular'].astype(int) # Pastikan 0 atau 1

        print(f"✅ Berhasil mengekstrak {len(df)} baris data.")
        return df

    except Exception as e:
        print(f"❌ Terjadi kesalahan saat ETL: {str(e)}")
        return None

if __name__ == "__main__":
    df = run_etl()
    if df is not None:
        df.to_csv('movie_demand_data.csv', index=False)