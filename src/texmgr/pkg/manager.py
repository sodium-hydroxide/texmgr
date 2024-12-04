"""Package management functionality."""

import re
from pathlib import Path
from typing import List, Optional, Dict, Tuple

from ..utils.errors import PackageError, PackageNotFoundError, FileOperationError
from ..utils.logs import logger
from ..utils.cmds import run_command, check_command_exists
from ..utils.fileops import find_file

def parse_package_line(line: str) -> List[Tuple[str, Optional[str]]]:
    """
    Parse a single \usepackage line to extract package names and options.

    Parameters
    ----------
    line : str
        Line containing \usepackage command

    Returns
    -------
    List[Tuple[str, Optional[str]]]
        List of tuples containing (package_name, options)
    """
    # Match \usepackage[options]{package} or \usepackage{package}
    pattern = r'\\usepackage(?:\[([^\]]*)\])?\{([^}]+)\}'
    match = re.match(pattern, line.strip())

    if not match:
        return []

    options = match.group(1)  # Could be None if no options
    packages = match.group(2).split(',')

    # Return list of (package, options) tuples
    return [(pkg.strip(), options) for pkg in packages if pkg.strip()]

def parse_packages(content: str) -> List[Tuple[str, Optional[str]]]:
    """
    Parse package names and their options from packages.tex content.

    Parameters
    ----------
    content : str
        Content of packages.tex file

    Returns
    -------
    List[Tuple[str, Optional[str]]]
        List of tuples containing (package_name, options)
    """
    packages = []

    # Process line by line for better error handling and logging
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('\\usepackage'):
            try:
                line_packages = parse_package_line(line)
                packages.extend(line_packages)

                # Log packages with options for debugging
                for pkg, opts in line_packages:
                    if opts:
                        logger.debug(f"Found package {pkg} with options: [{opts}]")
                    else:
                        logger.debug(f"Found package {pkg}")

            except Exception as e:
                logger.warning(f"Failed to parse package line: {line}")
                logger.debug(f"Parse error: {str(e)}")
                continue

    return packages

def read_packages_file() -> List[Tuple[str, Optional[str]]]:
    """
    Read and parse packages from packages.tex file.

    Returns
    -------
    List[Tuple[str, Optional[str]]]
        List of tuples containing (package_name, options)

    Raises
    ------
    FileOperationError
        If packages.tex file cannot be found or read
    """
    # Look for packages.tex in format directory
    packages_file = find_file(Path.cwd(), "format/packages.tex")
    if not packages_file:
        raise FileOperationError("Could not find packages.tex in project")

    try:
        content = packages_file.read_text()
        return parse_packages(content)
    except Exception as e:
        raise FileOperationError(f"Failed to read packages.tex: {str(e)}")

def install_package(package: str, options: Optional[str] = None) -> None:
    """
    Install a LaTeX package using tlmgr.

    Parameters
    ----------
    package : str
        Name of the package to install
    options : Optional[str]
        Package options (logged but not used for installation)

    Raises
    ------
    PackageError
        If package installation fails
    """
    if not check_command_exists("tlmgr"):
        raise PackageError("tlmgr not found. Please install TeX Live first")

    try:
        msg = f"Installing package: {package}"
        if options:
            msg += f" (used with options: [{options}])"
        logger.info(msg)

        run_command(
            ["tlmgr", "install", package],
            error_msg=f"Failed to install package {package}"
        )
    except Exception as e:
        raise PackageError(f"Failed to install package {package}: {str(e)}")

def handle_package_command(command: str, args) -> int:
    """
    Handle package-related commands.

    Parameters
    ----------
    command : str
        Package command to execute ('install')
    args : argparse.Namespace
        Command arguments

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """
    try:
        if command == "install":
            # Get packages from packages.tex
            packages = read_packages_file()
            logger.info(f"Found {len(packages)} packages to install")

            # Install each package
            for package, options in packages:
                try:
                    install_package(package, options)
                except PackageError as e:
                    logger.warning(f"Failed to install {package}: {str(e)}")
                    continue

            logger.info("Package installation complete")
            return 0

    except Exception as e:
        logger.error(str(e))
        return 1
