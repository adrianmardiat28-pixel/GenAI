from google import genai

# Masukkan API Key terbaru dari image_78a7ad.png
client = genai.Client(api_key="AIzaSyBrV7Z9pP8JQKpNFihQrOMAdydd_Ri4oHc".strip())

try:
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Tes koneksi untuk dashboard Adrian"
    )
    print(f"✅ Sukses! Respon AI: {response.text}")
except Exception as e:
    print(f"❌ Masih Error: {e}")