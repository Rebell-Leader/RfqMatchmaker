import os
import subprocess
import time
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

def start_streamlit():
    """Start the Streamlit application"""
    print("Starting Streamlit application...")
    streamlit_process = subprocess.Popen(
        ["streamlit", "run", "streamlit_frontend/Home.py", "--server.port", "8501"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    return streamlit_process

def main():
    # Create any necessary directories
    os.makedirs("uploads", exist_ok=True)
    
    # Start the FastAPI server
    fastapi_process = start_fastapi_server()
    
    try:
        # Start the Streamlit application
        streamlit_process = start_streamlit()
        
        # Print the URLs
        print("\n===== RFQ Processor Platform =====")
        print("FastAPI server running at: http://localhost:8000")
        print("API documentation available at: http://localhost:8000/docs")
        print("Streamlit frontend running at: http://localhost:8501")
        print("=====================================\n")
        
        # Monitor the processes
        while True:
            # Check if processes are still running
            if fastapi_process.poll() is not None:
                print("FastAPI server stopped. Restarting...")
                fastapi_process = start_fastapi_server()
            
            if streamlit_process.poll() is not None:
                print("Streamlit application stopped. Restarting...")
                streamlit_process = start_streamlit()
            
            # Read and print output from FastAPI
            fastapi_line = fastapi_process.stdout.readline()
            if fastapi_line:
                print("[FastAPI]", fastapi_line.strip())
                
            # Read and print output from Streamlit
            streamlit_line = streamlit_process.stdout.readline()
            if streamlit_line:
                print("[Streamlit]", streamlit_line.strip())
                
            # Prevent high CPU usage
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Terminate processes
        print("Terminating FastAPI server...")
        fastapi_process.terminate()
        
        print("Terminating Streamlit application...")
        streamlit_process.terminate()
        
        print("Cleanup complete. Goodbye!")

if __name__ == "__main__":
    main()