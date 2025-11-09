#!/usr/bin/env python3
"""
Development startup script for PulseCompass
Starts both backend and frontend servers
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def start_backend():
    """Start FastAPI backend server"""
    print("🚀 Starting FastAPI backend server...")
    backend_dir = Path(__file__).parent / "backend"
    
    # Install backend dependencies if needed
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      cwd=backend_dir, check=True, capture_output=True)
        print("✅ Backend dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Could not install backend dependencies: {e}")
    
    # Start backend server
    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "main:app", 
        "--host", "0.0.0.0", "--port", "8000", "--reload"
    ], cwd=backend_dir)
    
    print("🔗 Backend server starting at http://localhost:8000")
    return backend_process

def start_frontend():
    """Start Next.js frontend server"""
    print("🎨 Starting Next.js frontend server...")
    frontend_dir = Path(__file__).parent
    
    # Install frontend dependencies if needed
    try:
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True, capture_output=True)
        print("✅ Frontend dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Could not install frontend dependencies: {e}")
    
    # Start frontend server
    frontend_process = subprocess.Popen(["npm", "run", "dev"], cwd=frontend_dir)
    
    print("🔗 Frontend server starting at http://localhost:3000")
    return frontend_process

def main():
    """Main startup function"""
    print("🌟 PulseCompass Development Server Startup")
    print("=" * 50)
    
    # Check if Node.js is available
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ Node.js and npm are required for the frontend")
        print("📥 Please install Node.js from https://nodejs.org/")
        return
    
    # Start servers
    backend_process = start_backend()
    time.sleep(3)  # Give backend time to start
    frontend_process = start_frontend()
    
    print("\n" + "=" * 50)
    print("✅ Both servers are starting up!")
    print("🔗 Backend API: http://localhost:8000")
    print("🔗 Frontend UI: http://localhost:3000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\n💡 Press Ctrl+C to stop both servers")
    
    try:
        # Wait for both processes
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Servers stopped")

if __name__ == "__main__":
    main()
