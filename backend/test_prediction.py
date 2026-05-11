# Test script untuk prediction endpoint
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_predict():
    """Test /api/predict_advanced endpoint"""
    print("=" * 60)
    print("🧪 Testing /api/predict_advanced endpoint")
    print("=" * 60)
    
    payload = {
        "genre": "Action",
        "rating": "PG",
        "rental_duration": 5,
        "rental_rate": 2.99,
        "length": 120,
        "replacement_cost": 19.99
    }
    
    print(f"\n📤 Sending request to {BASE_URL}/api/predict_advanced")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/predict_advanced",
            json=payload,
            timeout=10
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📊 Response Body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS!")
            print(f"   - Prediction: {data.get('prediction')} {'(LARIS)' if data.get('prediction') == 1 else '(SEPI)'}")
            print(f"   - Confidence: {data.get('confidence', 0):.2%}")
            print(f"   - Prob Laris: {data.get('prob_laris', 0):.2%}")
            print(f"   - Prob Sepi: {data.get('prob_sepi', 0):.2%}")
        else:
            print(f"\n❌ ERROR: {response.json().get('detail', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ Connection error: {e}")
        print("   Make sure FastAPI server is running on port 8000")

def test_stats():
    """Test /api/predict_stats endpoint"""
    print("\n" + "=" * 60)
    print("🧪 Testing /api/predict_stats endpoint")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/predict_stats", timeout=10)
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS!")
            print(f"   - Rating Distribution: {len(data.get('rating_dist', []))} ratings")
            print(f"   - Top Winners: {len(data.get('winners', []))} genres")
            print(f"   - Top Losers: {len(data.get('losers', []))} genres")
        else:
            print(f"\n❌ ERROR: {response.json().get('detail', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ Connection error: {e}")

if __name__ == "__main__":
    print("\n🚀 Starting Prediction API Tests...\n")
    
    # Test both endpoints
    test_predict()
    test_stats()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
