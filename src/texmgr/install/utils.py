"""Utility functions for TeX Live installation."""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

from ..utils.errors import InstallError

def check_command_exists(command: str) -> bool:
    """
    Check if a command exists in the system PATH.

    Parameters
    ----------
    command : str
        Command to check

    Returns
    -------
    bool
        True if command exists, False otherwise
    """
    return shutil.which(command) is not None


def run_command(
    cmd: List[str],
    cwd: Optional[Path] = None,
    error_msg: str = "Command failed"
) -> subprocess.CompletedProcess:
    """
    Run a shell command safely.

    Parameters
    ----------
    cmd : List[str]
        Command and arguments to run
    cwd : Optional[Path]
        Working directory for the command
    error_msg : str
        Error message prefix if command fails

    Returns
    -------
    subprocess.CompletedProcess
        Completed process information

    Raises
    ------
    InstallError
        If command execution fails
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        raise InstallError(f"{error_msg}: {e.stderr}")
    except Exception as e:
        raise InstallError(f"{error_msg}: {str(e)}")


def get_texlive_path() -> Optional[Path]:
    """
    Get the path to TeX Live installation.

    Returns
    -------
    Optional[Path]
        Path to TeX Live installation if found, None otherwise
    """
    if check_command_exists("kpsewhich"):
        try:
            result = run_command(["kpsewhich", "-var-value", "TEXMFROOT"])
            return Path(result.stdout.strip())
        except InstallError:
            pass
    return None


def check_write_permission(path: Path) -> bool:
    """
    Check if we have write permission for a path.

    Parameters
    ----------
    path : Path
        Path to check

    Returns
    -------
    bool
        True if we have write permission, False otherwise
    """
    if path.exists():
        return os.access(path, os.W_OK)
    try:
        path.mkdir(parents=True, exist_ok=True)
        path.rmdir()
        return True
    except (OSError, PermissionError):
        return False
