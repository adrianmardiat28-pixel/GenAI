from sqlalchemy import create_engine
import pandas as pd

# ==========================================
# KONFIGURASI DATABASE (Sesuaikan di sini)
# ==========================================
DB_USER = "postgres"
DB_PASSWORD = "adrian280406"  # Teman kelompok bisa ganti ini saat run di lokal masing-masing
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "dvdrental"          
# ==========================================

def get_engine():
    """Membuat koneksi engine SQLAlchemy"""
    url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url)

# Inisialisasi engine di luar fungsi agar bisa melakukan Connection Pooling secara efisien
engine = get_engine()

def fetch_data(query):
    """Fungsi umum untuk mengambil data menggunakan Pandas"""
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        # Tampilkan error di Terminal Backend, bukan di UI
        print(f"❌ Koneksi/Query Database Gagal: {e}")
        return None