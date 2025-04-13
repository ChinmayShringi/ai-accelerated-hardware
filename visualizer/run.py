import sys
import os
import subprocess

if __name__ == "__main__":
    # Get the absolute path to app.py
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "app.py")
    
    # Run streamlit directly with file watcher disabled
    cmd = ["streamlit", "run", app_path, "--server.fileWatcherType=none"]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1) 