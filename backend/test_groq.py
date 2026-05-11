import httpx
import json

GROQ_API_KEY = "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"
URL = "https://api.groq.com/openai/v1/chat/completions"

def test_groq():
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": "Tes koneksi Groq untuk dashboard Adrian"}],
        "temperature": 0.7
    }

    try:
        with httpx.Client() as client:
            response = client.post(URL, headers=headers, json=data, timeout=20)
            result = response.json()
            print("✅ Sukses! Respon Groq:", result['choices'][0]['message']['content'])
    except Exception as e:
        print("❌ Error:", str(e))

if __name__ == "__main__":
    test_groq()