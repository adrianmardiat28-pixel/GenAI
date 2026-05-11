# 🧠 PREDICTION SYSTEM - SETUP GUIDE

## ⚠️ MASALAH: Prediksi Menampilkan NaN

Jika prediction page menampilkan NaN, ikuti langkah ini:

---

## ✅ STEP-BY-STEP FIX

### **Step 1: Train/Retrain Model**
```bash
cd backend
python train_model.py
```

Pastikan output terakhir:
```
📦 Model 'Super Cerdas' berhasil disimpan sebagai movie_demand_bundle.pkl
```

### **Step 2: Verify Model Files**
Pastikan file ini ada di folder `backend/`:
- ✅ `movie_demand_bundle.pkl` (Model file)
- ✅ `movie_demand_data.csv` (Training data)
- ✅ `predict_api.py` (Updated dengan path handling)
- ✅ `app.py` (Updated dengan health check)

### **Step 3: Check Health Endpoint**
```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "ml_model": "ready",
  "message": "✅ API Online"
}
```

### **Step 4: Test Prediction Endpoint**
```bash
cd backend
python test_predict_endpoint.py
```

Should show:
```
✅ SUCCESS! Parsed JSON:
{
  "prediction": 1,
  "confidence": 0.597,
  "prob_laris": 0.597,
  "prob_sepi": 0.403
}
```

### **Step 5: Start Server & Test Frontend**
```bash
# Terminal 1 - Start server
cd backend
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 - Open browser
# Navigate to: http://localhost:8080/frontend/prediction.html
# (or your frontend URL)
```

---

## 🔍 DEBUGGING - Jika Still Error

### Check Server Logs
Look for messages like:
- `[OK] ✅ ML Model Loaded Successfully` ✅
- `[ERROR] ❌ Model file tidak ditemukan` ❌

### Check Browser Console
Press `F12` → Console tab, look for:
- Network errors → Check server running
- JSON parse errors → Check response format
- NaN validation errors → Check backend response

### Test with curl
```bash
curl -X POST http://127.0.0.1:8000/api/predict_advanced \
  -H "Content-Type: application/json" \
  -d '{
    "genre": "Action",
    "rating": "PG",
    "rental_duration": 5,
    "rental_rate": 2.99,
    "length": 120,
    "replacement_cost": 19.99
  }'
```

Expected response (valid JSON, NO NaN):
```json
{
  "prediction": 1,
  "confidence": 0.5969516,
  "prob_laris": 0.5969516,
  "prob_sepi": 0.4030483
}
```

---

## 📋 CHECKLIST

- [ ] Model file exists: `backend/movie_demand_bundle.pkl`
- [ ] Data file exists: `backend/movie_demand_data.csv`  
- [ ] Model trained: `python train_model.py` (Output shows success)
- [ ] predict_api.py updated with proper error handling
- [ ] Health endpoint works: `curl http://127.0.0.1:8000/health`
- [ ] Prediction endpoint returns valid JSON (no NaN)
- [ ] Frontend shows confidence % correctly
- [ ] Donut chart renders properly

---

## 🚀 QUICK START (TL;DR)

```bash
# Step 1: Re-train model
cd backend
python train_model.py

# Step 2: Start server
python -m uvicorn app:app --reload

# Step 3: Test endpoint
python test_predict_endpoint.py

# Step 4: Open browser
# http://localhost:8080/frontend/prediction.html
```

---

## 📞 If Still Not Working

1. **Delete old model file and retrain:**
   ```bash
   rm backend/movie_demand_bundle.pkl
   python backend/train_model.py
   ```

2. **Restart FastAPI server completely:**
   - Close terminal
   - Kill any Python processes
   - Start fresh: `python -m uvicorn app:app --reload`

3. **Check Python version:**
   ```bash
   python --version  # Should be 3.8+
   ```

4. **Check installed packages:**
   ```bash
   pip list | grep -E "scikit-learn|joblib|fastapi|pandas"
   ```

---

**Last Updated:** May 12, 2026
**Status:** ✅ Tested & Working
