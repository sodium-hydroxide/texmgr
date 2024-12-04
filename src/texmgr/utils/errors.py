"""
Custom exceptions for texmgr.

Notes
-----
Hierarchy of exceptions:
- TexmgrError (base)
    - InstallError
        - TexLiveError
        - DependencyError
    - ProjectError
        - InitError
        - BuildError
    - PackageError
        - PackageNotFoundError
        - PackageInstallError
"""


class TexmgrError(Exception):
    """
    Base exception for texmgr.

    Parameters
    ----------
    message : str
        Error message
    exit_code : int, optional
        Exit code to use when this error occurs, by default 1
    """

    def __init__(self, message: str, exit_code: int = 1):
        self.message = message
        self.exit_code = exit_code
        super().__init__(self.message)


# Installation related errors
class InstallError(TexmgrError):
    """Base class for installation related errors."""

    pass


class TexLiveError(InstallError):
    """Errors related to TeX Live installation or operation."""

    pass


class DependencyError(InstallError):
    """Errors related to missing or incompatible dependencies."""

    pass


# Project related errors
class ProjectError(TexmgrError):
    """Base class for project related errors."""

    pass


class InitError(ProjectError):
    """Errors during project initialization."""

    pass


class BuildError(ProjectError):
    """Errors during document building."""

    pass


class FileOperationError(ProjectError):
    """Errors during file operations."""

    pass


# Package related errors
class PackageError(TexmgrError):
    """Base class for package related errors."""

    pass


class PackageNotFoundError(PackageError):
    """Package not found in CTAN or local installation."""

    pass


class PackageInstallError(PackageError):
    """Errors during package installation."""

    pass


# Function to get appropriate error class based on error type
def get_error_class(error_type: str) -> type:
    """
    Get the appropriate error class based on error type.

    Parameters
    ----------
    error_type : str
        Type of error to get class for

    Returns
    -------
    type
        Error class to use

    Raises
    ------
    ValueError
        If error_type is not recognized
    """
    error_classes = {
        "texlive": TexLiveError,
        "dependency": DependencyError,
        "init": InitError,
        "build": BuildError,
        "file": FileOperationError,
        "package": PackageError,
        "package_not_found": PackageNotFoundError,
        "package_install": PackageInstallError,
    }

    if error_type not in error_classes:
        raise ValueError(f"Unknown error type: {error_type}")

    return error_classes[error_type]
