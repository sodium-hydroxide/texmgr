"""Logging configuration for texmgr."""

import logging
import sys
from pathlib import Path
from typing import Optional

# ANSI color codes
COLORS = {
    "BLUE": "\033[94m",
    "ORANGE": "\033[93m",
    "RED": "\033[91m",
    "RESET": "\033[0m",
}


class ColoredFormatter(logging.Formatter):
    """A custom formatter that adds colors to log messages based on level."""

    LEVEL_COLORS = {
        logging.INFO: COLORS["BLUE"],
        logging.WARNING: COLORS["ORANGE"],
        logging.ERROR: COLORS["RED"],
        logging.CRITICAL: COLORS["RED"],
    }

    def format(self, record):
        """
        Format the log record with appropriate color.

        Parameters
        ----------
        record : logging.LogRecord
            The log record to format

        Returns
        -------
        str
            The formatted log message with color codes
        """
        # Add color if the level is INFO or higher and we're not in debug mode
        if record.levelno >= logging.INFO:
            color = self.LEVEL_COLORS.get(record.levelno, "")
            record.msg = f"{color}{record.msg}{COLORS['RESET']}"

        return super().format(record)


def find_project_root() -> Optional[Path]:
    """
    Find the root directory of the current LaTeX project.

    Returns
    -------
    Optional[Path]
        Path to project root if found, None otherwise

    Notes
    -----
    Project root is identified by the presence of a main.tex file
    """
    current = Path.cwd()

    # Look for main.tex in current or parent directories
    while current != current.parent:
        if (current / "main.tex").exists():
            return current
        current = current.parent

    return None


def setup_logging(verbose: bool = False) -> logging.Logger:
    """
    Setup logging configuration.

    Parameters
    ----------
    verbose : bool, optional
        If True, set logging level to DEBUG, by default False

    Returns
    -------
    logging.Logger
        Logger instance configured for the application

    Notes
    -----
    - Configures both file and console logging
    - Console logging uses colors for INFO and above
    - File logging includes all debug messages
    - Logs are stored in project_root/output/logs/ if in a project,
      otherwise in ~/.texmgr/logs/
    """
    logger = logging.getLogger("texmgr")

    # Set the logging level based on verbosity
    level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(level)

    # Create formatters
    console_formatter = ColoredFormatter("%(message)s")
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(level)

    # Determine log directory
    project_root = find_project_root()
    if project_root:
        log_dir = project_root / "output" / "logs"
    else:
        log_dir = Path.home() / ".texmgr" / "logs"

    # Create log directory
    log_dir.mkdir(parents=True, exist_ok=True)

    # File handler
    file_handler = logging.FileHandler(log_dir / "texmgr.log")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)  # Always log debug to file

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
