"""
Simplified start script for Railway - Streamlit only with embedded FastAPI
"""
import os
import sys
import subprocess

# Get PORT from Railway
port = int(os.environ.get("PORT", 8501))

# Set backend URL to use local FastAPI
os.environ["BACKEND_URL"] = f"http://localhost:8000"

# Start Streamlit on Railway's assigned port
subprocess.run([
    sys.executable, "-m", "streamlit", "run",
    "frontend/streamlit_app.py",
    "--server.port", str(port),
    "--server.address", "0.0.0.0",
    "--server.headless", "true"
])