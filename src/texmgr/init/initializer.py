"""Project initialization functionality."""

import subprocess
from pathlib import Path
from typing import Optional

from ..utils.errors import InitError, FileOperationError
from ..utils.logs import logger
from ..utils.cmds import run_command
from ..utils.fileops import ensure_dir, safe_write, create_project_structure
from ..config import PROJECT_DIRS, get_template_files

def init_git(project_dir: Path) -> None:
    """
    Initialize a git repository in the project directory.

    Parameters
    ----------
    project_dir : Path
        Project directory

    Raises
    ------
    InitError
        If git initialization fails
    """
    try:
        logger.info("Initializing git repository...")
        run_command(
            ["git", "init"],
            cwd=project_dir,
            error_msg="Failed to initialize git repository"
        )
    except Exception as e:
        raise InitError(f"Failed to initialize git repository: {str(e)}")

def create_project_files(project_dir: Path, doc_type: str) -> None:
    """
    Create project files from templates.

    Parameters
    ----------
    project_dir : Path
        Project directory
    doc_type : str
        Type of document ('article' or 'beamer')

    Raises
    ------
    InitError
        If file creation fails
    FileOperationError
        If template is not found
    """
    try:
        templates = get_template_files(doc_type)
    except ValueError as e:
        raise InitError(str(e))

    logger.info(f"Creating {doc_type} project files...")

    for file_path, content in templates.items():
        try:
            full_path = project_dir / file_path
            # Create parent directories if needed
            ensure_dir(full_path.parent)
            safe_write(full_path, content)
            logger.debug(f"Created {file_path}")
        except FileOperationError as e:
            raise InitError(f"Failed to create {file_path}: {str(e)}")

def init_project(use_git: bool = True, doc_type: str = "article") -> int:
    """
    Initialize a new LaTeX project.

    Parameters
    ----------
    use_git : bool, optional
        Whether to initialize git repository, by default True
    doc_type : str, optional
        Type of document to create, by default "article"

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """
    try:
        project_dir = Path.cwd()

        # Check if directory is empty
        if any(project_dir.iterdir()):
            raise InitError(
                "Directory is not empty. Please use an empty directory for initialization."
            )

        logger.info(f"Initializing new {doc_type} project...")

        # Create project structure
        create_project_structure(project_dir, PROJECT_DIRS)

        # Create project files
        create_project_files(project_dir, doc_type)

        # Initialize git if requested
        if use_git:
            init_git(project_dir)

        logger.info("Project initialization complete!")
        return 0

    except Exception as e:
        logger.error(str(e))
        return 1
