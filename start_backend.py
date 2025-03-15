"""
Startup script for the RFQ processing platform.
This script starts both the FastAPI backend and the TypeScript frontend.
"""

import os
import subprocess
import time
import signal
import sys

def start_fastapi_server():
    """Start the FastAPI server in a separate process"""
    print("Starting FastAPI server...")
    fastapi_process = subprocess.Popen(
        ["python", "-m", "python_backend.main"], 
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    # Wait a moment for the server to start
    time.sleep(2)
    return fastapi_process

def main():
    # Create any necessary directories
    os.makedirs("uploads", exist_ok=True)
    
    # Start the FastAPI server
    fastapi_process = start_fastapi_server()
    
    try:
        # Print the URLs
        print("\n===== RFQ Processor Platform =====")
        print("FastAPI server running at: http://localhost:8000")
        print("API documentation available at: http://localhost:8000/docs")
        print("=====================================\n")
        
        # Monitor the FastAPI process
        while True:
            # Check if process is still running
            if fastapi_process.poll() is not None:
                print("FastAPI server stopped. Restarting...")
                fastapi_process = start_fastapi_server()
            
            # Read and print output from FastAPI
            fastapi_line = fastapi_process.stdout.readline()
            if fastapi_line:
                print("[FastAPI]", fastapi_line.strip())
            
            # Prevent high CPU usage
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Terminate process
        print("Terminating FastAPI server...")
        fastapi_process.terminate()
        
        print("Cleanup complete. Goodbye!")

if __name__ == "__main__":
    main()