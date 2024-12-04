"""Utility functions for file operations."""

import shutil
from pathlib import Path
from typing import Union, List, Optional
import logging

from .errors import FileOperationError

logger = logging.getLogger("texmgr")


def ensure_dir(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, create it if it doesn't.

    Parameters
    ----------
    path : Union[str, Path]
        Path to the directory

    Returns
    -------
    Path
        Path object pointing to the directory

    Raises
    ------
    FileOperationError
        If directory creation fails or path exists but is not a directory
    """
    path = Path(path)
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise FileOperationError(f"Failed to create directory {path}: {str(e)}")

    if not path.is_dir():
        raise FileOperationError(f"Path exists but is not a directory: {path}")

    return path


def safe_copy(
    src: Union[str, Path], dst: Union[str, Path], overwrite: bool = False
) -> Path:
    """
    Safely copy a file.

    Parameters
    ----------
    src : Union[str, Path]
        Source file path
    dst : Union[str, Path]
        Destination file path
    overwrite : bool, optional
        Whether to overwrite existing files, by default False

    Returns
    -------
    Path
        Path to the copied file

    Raises
    ------
    FileOperationError
        If copy operation fails or source file doesn't exist
    """
    src, dst = Path(src), Path(dst)

    if not src.exists():
        raise FileOperationError(f"Source file does not exist: {src}")

    if dst.exists() and not overwrite:
        raise FileOperationError(f"Destination file already exists: {dst}")

    try:
        # Ensure the parent directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    except Exception as e:
        raise FileOperationError(f"Failed to copy {src} to {dst}: {str(e)}")

    return dst


def safe_write(path: Union[str, Path], content: str, overwrite: bool = False) -> Path:
    """
    Safely write content to a file.

    Parameters
    ----------
    path : Union[str, Path]
        Path to write to
    content : str
        Content to write
    overwrite : bool, optional
        Whether to overwrite existing files, by default False

    Returns
    -------
    Path
        Path to the written file

    Raises
    ------
    FileOperationError
        If write operation fails or file exists and overwrite is False
    """
    path = Path(path)

    if path.exists() and not overwrite:
        raise FileOperationError(f"File already exists: {path}")

    try:
        # Ensure the parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    except Exception as e:
        raise FileOperationError(f"Failed to write to {path}: {str(e)}")

    return path


def create_project_structure(root: Union[str, Path], dirs: List[str]) -> None:
    """
    Create a project directory structure.

    Parameters
    ----------
    root : Union[str, Path]
        Root directory for the project
    dirs : List[str]
        List of directories to create relative to root

    Raises
    ------
    FileOperationError
        If directory creation fails
    """
    root = Path(root)

    for dir_path in dirs:
        ensure_dir(root / dir_path)


def find_file(
    start_path: Union[str, Path], filename: str, max_depth: int = 5
) -> Optional[Path]:
    """
    Find a file by name starting from a given directory.

    Parameters
    ----------
    start_path : Union[str, Path]
        Directory to start searching from
    filename : str
        Name of the file to find
    max_depth : int, optional
        Maximum directory depth to search, by default 5

    Returns
    -------
    Optional[Path]
        Path to the file if found, None otherwise
    """
    start_path = Path(start_path)

    if not start_path.is_dir():
        logger.debug(f"Start path is not a directory: {start_path}")
        return None

    try:
        current_path = start_path
        for _ in range(max_depth + 1):
            file_path = current_path / filename
            if file_path.is_file():
                return file_path

            if current_path == current_path.parent:  # Reached root
                break

            current_path = current_path.parent

    except Exception as e:
        logger.debug(f"Error while searching for {filename}: {str(e)}")

    return None


def clean_directory(
    path: Union[str, Path], exclude: Optional[List[str]] = None
) -> None:
    """
    Clean a directory by removing all its contents except excluded items.

    Parameters
    ----------
    path : Union[str, Path]
        Directory to clean
    exclude : Optional[List[str]], optional
        List of items to exclude from cleaning, by default None

    Raises
    ------
    FileOperationError
        If cleaning operation fails
    """
    path = Path(path)
    exclude = exclude or []

    if not path.is_dir():
        raise FileOperationError(f"Not a directory: {path}")

    try:
        for item in path.iterdir():
            if item.name in exclude:
                continue

            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
    except Exception as e:
        raise FileOperationError(f"Failed to clean directory {path}: {str(e)}")


def detect_project_root(
    start_path: Optional[Union[str, Path]] = None,
) -> Optional[Path]:
    """
    Detect the root directory of a LaTeX project.

    Parameters
    ----------
    start_path : Optional[Union[str, Path]], optional
        Path to start searching from, by default current directory

    Returns
    -------
    Optional[Path]
        Path to project root if found, None otherwise

    Notes
    -----
    A directory is considered a project root if it contains a main.tex file
    """
    start_path = Path(start_path or Path.cwd())
    result = find_file(start_path, "main.tex")
    return result.parent if result else None


def is_valid_project_dir(path: Union[str, Path]) -> bool:
    """
    Check if a directory is a valid LaTeX project directory.

    Parameters
    ----------
    path : Union[str, Path]
        Directory to check

    Returns
    -------
    bool
        True if directory is a valid project directory, False otherwise

    Notes
    -----
    A valid project directory must contain:
    - main.tex file
    - format/ directory
    - output/ directory
    - text/ directory
    """
    path = Path(path)

    required_files = ["main.tex"]
    required_dirs = ["format", "output", "text"]

    # Check if all required files exist
    for file in required_files:
        if not (path / file).is_file():
            logger.debug(f"Required file missing: {file}")
            return False

    # Check if all required directories exist
    for dir_name in required_dirs:
        if not (path / dir_name).is_dir():
            logger.debug(f"Required directory missing: {dir_name}")
            return False

    return True
