import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple, Union

def mkdir(path: Union[str, Path], parents: bool = True) -> None:
    """Create a directory if it doesn't exist."""
    Path(path).mkdir(parents=parents, exist_ok=True)

def mv(src: Union[str, Path], dst: Union[str, Path]) -> None:
    """Move a file or directory."""
    shutil.move(str(src), str(dst))

def rm(path: Union[str, Path]) -> None:
    """Remove a file or directory."""
    path = Path(path)
    if path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)

def cp(src: Union[str, Path], dst: Union[str, Path]) -> None:
    """Copy a file or directory."""
    src = Path(src)
    dst = Path(dst)
    if src.is_file():
        shutil.copy2(src, dst)
    elif src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)

def run(command: str, cwd: Optional[str] = None, ignore_errors: bool = False) -> Optional[str]:
    """
    Run a shell command and return the stdout if successful.
    
    Args:
        command: Command string to execute
        cwd: Working directory to run the command in
        ignore_errors: If True, return None on error instead of raising an exception
        
    Returns:
        Command output as string if successful, None if ignore_errors is True and command failed
    """
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            text=True
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0 and not ignore_errors:
            raise subprocess.CalledProcessError(process.returncode, command, stdout, stderr)
        return stdout.strip() if stdout else None
    except subprocess.CalledProcessError:
        if ignore_errors:
            return None
        raise 