#!/bin/bash
# Start script that ensures correct port
streamlit run app_minimal.py --server.port ${PORT:-8501} --server.address 0.0.0.0 --server.headless true