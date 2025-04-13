import os
from pathlib import Path

def synth_path() -> Path:
    """Return the path to the RTL directory."""
    return Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))) / 'rtl' 