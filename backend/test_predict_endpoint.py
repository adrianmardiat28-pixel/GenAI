#!/usr/bin/env python
# backend/test_predict_endpoint.py
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 70)
print("🧪 TESTING PREDICTION ENDPOINT")
print("=" * 70)

# Test request
payload = {
    "genre": "Action",
    "rating": "PG",
    "rental_duration": 5,
    "rental_rate": 2.99,
    "length": 120,
    "replacement_cost": 19.99
}

print(f"\n📤 Sending POST request to {BASE_URL}/api/predict_advanced")
print(f"📦 Payload:\n{json.dumps(payload, indent=2)}")

try:
    response = requests.post(
        f"{BASE_URL}/api/predict_advanced",
        json=payload,
        timeout=10
    )
    
    print(f"\n📊 Response Status: {response.status_code}")
    print(f"📊 Response Headers: {dict(response.headers)}")
    
    print(f"\n📝 Raw Response Text:")
    print(response.text)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS! Parsed JSON:")
        print(json.dumps(data, indent=2))
        
        # Validate values
        import math
        errors = []
        
        if "prediction" not in data:
            errors.append("Missing 'prediction' field")
        elif not isinstance(data["prediction"], (int, float)):
            errors.append(f"'prediction' should be number, got {type(data['prediction'])}")
        
        if "confidence" not in data:
            errors.append("Missing 'confidence' field")
        elif math.isnan(data["confidence"]):
            errors.append("'confidence' is NaN!")
        elif not (0 <= data["confidence"] <= 1):
            errors.append(f"'confidence' out of range [0,1]: {data['confidence']}")
        
        if "prob_laris" not in data:
            errors.append("Missing 'prob_laris' field")
        elif math.isnan(data["prob_laris"]):
            errors.append("'prob_laris' is NaN!")
        
        if "prob_sepi" not in data:
            errors.append("Missing 'prob_sepi' field")
        elif math.isnan(data["prob_sepi"]):
            errors.append("'prob_sepi' is NaN!")
        
        if errors:
            print(f"\n⚠️ VALIDATION ERRORS:")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"\n✅ All values valid!")
            print(f"   - Prediction: {data['prediction']} ({'LARIS' if data['prediction'] == 1 else 'SEPI'})")
            print(f"   - Confidence: {data['confidence']:.2%}")
            print(f"   - Prob Laris: {data['prob_laris']:.2%}")
            print(f"   - Prob Sepi: {data['prob_sepi']:.2%}")
    else:
        print(f"\n❌ ERROR: {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error detail: {error_data.get('detail', 'N/A')}")
        except:
            print(f"Could not parse error response")

except Exception as e:
    print(f"\n❌ Connection Error: {e}")
    print("\nMake sure:")
    print("  1. FastAPI server is running: python -m uvicorn app:app --reload")
    print("  2. Server is listening on http://127.0.0.1:8000")
    print("  3. Backend folder has movie_demand_bundle.pkl")

print("\n" + "=" * 70)
