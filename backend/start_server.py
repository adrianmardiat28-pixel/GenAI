#!/usr/bin/env python
# backend/start_server.py
"""
Quick starter script untuk FastAPI server dengan debug info
"""
import os
import sys
import subprocess

print("""
╔════════════════════════════════════════════════════════════╗
║                  🚀 MOVIE API SERVER STARTER              ║
╚════════════════════════════════════════════════════════════╝
""")

# Check jika model exists
model_path = os.path.join(os.path.dirname(__file__), 'movie_demand_bundle.pkl')
print(f"✓ Checking model file...")
if os.path.exists(model_path):
    print(f"  ✅ Model found: {model_path}")
else:
    print(f"  ❌ Model NOT found: {model_path}")
    print(f"  ⚠️  Run 'python train_model.py' first!")
    sys.exit(1)

# Check jika data file exists
data_path = os.path.join(os.path.dirname(__file__), 'movie_demand_data.csv')
print(f"\n✓ Checking data file...")
if os.path.exists(data_path):
    print(f"  ✅ Data found: {data_path}")
else:
    print(f"  ⚠️  Data NOT found: {data_path}")

# Start server
print(f"\n✓ Starting FastAPI server...")
print(f"  → Listening on http://127.0.0.1:8000")
print(f"  → API Docs: http://127.0.0.1:8000/docs")
print(f"  → Press Ctrl+C to stop\n")

os.system("python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000")
