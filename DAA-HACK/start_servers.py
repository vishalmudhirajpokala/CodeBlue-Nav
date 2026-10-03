"""Start both CodeBlue Nav servers and open browser."""

import subprocess
import sys
import time
import os
import webbrowser

# Change to project directory
os.chdir(r"C:\Users\NIMISHAMBIKA\OneDrive\Desktop\DAA-HACK")

# Start backend
print("Starting backend...")
backend_proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "backend.app.main:app",
     "--host", "127.0.0.1", "--port", "8000", "--reload"],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
time.sleep(3)

# Start frontend
print("Starting frontend...")
frontend_proc = subprocess.Popen(
    [sys.executable, "-m", "vite", "dev"],
    cwd=os.path.join(r"C:\Users\NIMISHAMBIKA\OneDrive\Desktop\DAA-HACK", "frontend"),
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
time.sleep(3)

# Open browsers
print("Opening browsers...")
try:
    webbrowser.open("http://127.0.0.1:8000/graph")
    print("  -> Backend URL opened")
except Exception as e:
    print(f"  Backend open error: {e}")

try:
    webbrowser.open("http://localhost:5173")
    print("  -> Frontend URL opened")
except Exception as e:
    print(f"  Frontend open error: {e}")

print("\nServers running. Press Ctrl+C to stop.")
try:
    while True:
        time.sleep(15)
except KeyboardInterrupt:
    print("\nStopping servers...")
    backend_proc.terminate()
    frontend_proc.terminate()
    print("Done.")