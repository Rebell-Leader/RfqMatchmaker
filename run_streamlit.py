import os
import subprocess
import time

# Start the FastAPI backend
backend_process = subprocess.Popen(
    ["python", "-m", "uvicorn", "python_backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Give the backend a few seconds to start
print("Starting FastAPI backend...")
time.sleep(2)

# Start the Streamlit frontend
print("Starting Streamlit frontend...")
streamlit_process = subprocess.Popen(
    ["streamlit", "run", "streamlit_frontend/Home.py", "--server.port", "8501", "--server.address", "0.0.0.0"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Print URLs for accessing the applications
print("\n==== Application URLs ====")
print("FastAPI Backend: http://localhost:8000")
print("Streamlit Frontend: http://localhost:8501")
print("==========================\n")

try:
    # Keep the script running until interrupted
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # Terminate processes on keyboard interrupt
    print("Shutting down...")
    backend_process.terminate()
    streamlit_process.terminate()
    backend_process.wait()
    streamlit_process.wait()
    print("Done.")