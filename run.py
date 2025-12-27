import subprocess
import os
import sys
import signal
import time

def run_command(command, cwd=None, background=True):
    if background:
        return subprocess.Popen(command, shell=True, cwd=cwd)
    else:
        return subprocess.run(command, shell=True, cwd=cwd)

def main():
    print("🚀 Starting Baby Tracker Unified Suite...")

    # Start Backend
    print("📦 Starting Backend (FastAPI)...")
    backend_proc = run_command("uvicorn backend.main:app --host 0.0.0.0 --port 8000")

    # Start Frontend (Dev mode)
    print("🎨 Starting Frontend (Vite)...")
    # In a real build, we'd serve the static files, but for dev ease we'll use vite dev
    frontend_proc = run_command("npm run dev", cwd="frontend")

    # Start Telegram Bot
    print("🤖 Starting Telegram Bot...")
    # bot_proc = run_command("python telegram_bot.py")

    print("\n✅ All services are running!")
    print("👉 Backend API: http://localhost:8000")
    print("👉 Frontend Dashboard: http://localhost:5173 (or as shown by Vite)")
    print("Press Ctrl+C to stop all services.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping Baby Tracker Suite...")
        backend_proc.terminate()
        frontend_proc.terminate()
        # bot_proc.terminate()
        print("Done.")

if __name__ == "__main__":
    main()
