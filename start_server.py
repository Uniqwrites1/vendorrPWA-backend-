#!/usr/bin/env python3
"""
Simple server startup script for the FastAPI application
"""
import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    import uvicorn
    from app.main import app

    print("Starting Vendorr FastAPI server...")
    print(f"Current directory: {current_dir}")
    print("Server will be available at: http://127.0.0.1:8000")
    print("API Documentation at: http://127.0.0.1:8000/docs")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )
