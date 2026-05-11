# backend/train_model2.py
import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle
from database import fetch_data

def train_revenue_model():
    print("⏳ Mengambil data historis dari database PostgreSQL...")
    query = """
        SELECT DATE(payment_date) as date, SUM(amount) as daily_revenue
        FROM payment
        GROUP BY DATE(payment_date)
        ORDER BY date;
    """
    df = fetch_data(query)

    if df is not None and not df.empty:
        print("📈 Data berhasil diambil. Mulai melatih model Machine Learning...")
        
        df['date'] = pd.to_datetime(df['date'])
        
        min_date = df['date'].min()
        max_date = df['date'].max() # KITA SIMPAN TANGGAL TERAKHIR
        
        df['day_index'] = (df['date'] - min_date).dt.days

        X = df[['day_index']]
        y = df['daily_revenue']

        model = LinearRegression()
        model.fit(X, y)

        model_data = {
            'model': model,
            'min_date': min_date,
            'max_date': max_date 
        }

        with open('revenue_model.pkl', 'wb') as f:
            pickle.dump(model_data, f)
            
        print("✅ BERHASIL! Model AI telah disimpan dengan nama 'revenue_model.pkl'")
    else:
        print("❌ Gagal mengambil data. Pastikan database berjalan.")

if __name__ == "__main__":
    train_revenue_model()