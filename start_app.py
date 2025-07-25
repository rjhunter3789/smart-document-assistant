"""
Start both FastAPI backend and Streamlit frontend for Railway deployment
"""
import subprocess
import os
import time
import sys

def start_services():
    # Get PORT from environment (Railway provides this)
    port = int(os.environ.get("PORT", 8000))
    
    # Set backend URL for Streamlit to use
    os.environ["BACKEND_URL"] = f"http://localhost:{port}"
    
    # Start FastAPI backend
    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "backend.main:app",
        "--host", "0.0.0.0",
        "--port", str(port)
    ])
    
    print(f"Started FastAPI backend on port {port}")
    
    # Give backend time to start
    time.sleep(3)
    
    # Start Streamlit frontend on a different port
    streamlit_port = port + 1
    frontend_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run",
        "frontend/streamlit_app.py",
        "--server.port", str(streamlit_port),
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ])
    
    print(f"Started Streamlit frontend on port {streamlit_port}")
    
    # Wait for both processes
    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("Shutting down...")
        backend_process.terminate()
        frontend_process.terminate()

if __name__ == "__main__":
    start_services()