from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any

@dataclass
class Config:
    """Configuration for program synthesis."""
    
    def __init__(self):
        self.params: Dict[str, Any] = {}
        self.rtl_path: Path = Path()
        self.verilog_params: Dict[str, Any] = {}

# Create a global config instance
config = Config() 