# backend/train_model.py
import pandas as pd
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

def run_training():
    print("--- 🧠 Memulai Proses Training Model: Movie Demand Predictor ---")
    
    # 1. LOAD DATA DARI DATABASE (CSV hasil ETL)
    try:
        df = pd.read_csv('movie_demand_data.csv')
        print(f"✅ Berhasil memuat {len(df)} baris data historis.")
    except FileNotFoundError:
        print("❌ Error: File movie_demand_data.csv tidak ditemukan. Jalankan etl.py!")
        return

    # 2. LOGIC INJECTION (DINAMIS DARI DATABASE)
    print("💉 Menyuntikkan Logika Ekstrem (Anti-Bias Berdasarkan Data Asli)...")
    
    # Ambil 150 sampel acak dari data asli (mencakup semua genre & rating secara alami)
    df_sample = df.sample(n=150, random_state=42, replace=True).copy()

    # SKENARIO A: HARGA SEWA TIDAK MASUK AKAL (> $15) -> PASTI SEPI (0)
    df_extreme_rate = df_sample.copy()
    # Acak harga sewa dari $15 sampai $30
    df_extreme_rate['rental_rate'] = np.random.uniform(15.0, 30.0, size=len(df_extreme_rate))
    df_extreme_rate['is_popular'] = 0 

    # SKENARIO B: BIAYA GANTI RUGI SANGAT MAHAL (> $50) -> PASTI SEPI (0)
    df_extreme_cost = df_sample.copy()
    # Acak biaya ganti dari $50 sampai $150
    df_extreme_cost['replacement_cost'] = np.random.uniform(50.0, 150.0, size=len(df_extreme_cost))
    df_extreme_cost['is_popular'] = 0

    # Gabungkan data asli dengan data kloningan yang sudah dimanipulasi harganya
    df = pd.concat([df, df_extreme_rate, df_extreme_cost], ignore_index=True)
    print(f"Total data setelah augmentasi dinamis: {len(df)} baris.")

    # 3. FEATURE ENGINEERING (One-Hot Encoding)
    genre_dummies = pd.get_dummies(df['category_name'], prefix='genre')
    rating_dummies = pd.get_dummies(df['rating'], prefix='rating')
    df_final = pd.concat([df, genre_dummies, rating_dummies], axis=1)
    
    # 4. SELEKSI FITUR
    base_features = ['rental_duration', 'rental_rate', 'length', 'replacement_cost']
    features = base_features + list(genre_dummies.columns) + list(rating_dummies.columns)
    
    X = df_final[features]
    y = df_final['is_popular']

    # 5. SPLIT DATA
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 6. TRAINING DENGAN PENYETELAN
    model = RandomForestClassifier(
        n_estimators=500,
        max_depth=7, 
        min_samples_leaf=10,
        class_weight='balanced',
        random_state=42
    )
    
    print(f"⏳ Melatih model pada {len(features)} fitur...")
    model.fit(X_train, y_train)

    # 7. EVALUASI
    y_pred = model.predict(X_test)
    print("\n--- 📊 HASIL EVALUASI MODEL ---")
    print(f"Akurasi: {accuracy_score(y_test, y_pred) * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # 8. SIMPAN MODEL BUNDLE
    bundle = {
        'model': model,
        'features': features
    }
    joblib.dump(bundle, 'movie_demand_bundle.pkl')
    print("\n📦 Model 'Super Cerdas' berhasil disimpan sebagai movie_demand_bundle.pkl")

if __name__ == "__main__":
    run_training()