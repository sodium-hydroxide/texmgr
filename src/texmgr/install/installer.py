"""TeX Live installation management."""

import tempfile
import urllib.request
from pathlib import Path

from ..utils.errors import InstallError, DependencyError
from ..utils.logs import logger
from ..utils.cmds import (
    check_command_exists,
    run_command,
    get_platform,
    check_write_permission
)

TEXLIVE_MIRROR = "https://mirror.ctan.org/systems/texlive/tlnet"
INSTALL_SCRIPT = "install-tl-unx.tar.gz"

def download_texlive_installer() -> Path:
    """
    Download the TeX Live installer script.

    Returns
    -------
    Path
        Path to the downloaded installer

    Raises
    ------
    InstallError
        If download fails
    """
    logger.info("Downloading TeX Live installer...")
    temp_dir = Path(tempfile.mkdtemp())
    installer_path = temp_dir / INSTALL_SCRIPT

    try:
        url = f"{TEXLIVE_MIRROR}/{INSTALL_SCRIPT}"
        urllib.request.urlretrieve(url, installer_path)
        logger.debug(f"Downloaded installer to {installer_path}")
        return installer_path
    except Exception as e:
        raise InstallError(f"Failed to download TeX Live installer: {str(e)}")

def extract_installer(installer_path: Path) -> Path:
    """
    Extract the TeX Live installer.

    Parameters
    ----------
    installer_path : Path
        Path to the downloaded installer

    Returns
    -------
    Path
        Path to the extracted installer directory

    Raises
    ------
    InstallError
        If extraction fails
    """
    logger.info("Extracting TeX Live installer...")
    try:
        extract_dir = installer_path.parent
        run_command(
            ["tar", "xzf", installer_path],
            cwd=extract_dir,
            error_msg="Failed to extract installer"
        )

        # Find the extracted directory (should be install-tl-YYYYMMDD)
        install_dirs = [d for d in extract_dir.iterdir() if d.is_dir() and d.name.startswith("install-tl-")]
        if not install_dirs:
            raise InstallError("Could not find extracted installer directory")

        return install_dirs[0]
    except Exception as e:
        raise InstallError(f"Failed to extract installer: {str(e)}")

def create_profile(install_dir: Path) -> Path:
    """
    Create a TeX Live installation profile.

    Parameters
    ----------
    install_dir : Path
        Directory where TeX Live should be installed

    Returns
    -------
    Path
        Path to the created profile file

    Raises
    ------
    InstallError
        If profile creation fails
    """
    from ..config import TEXLIVE_PROFILE

    logger.info("Creating installation profile...")
    try:
        profile_path = install_dir / "texlive.profile"
        profile_content = TEXLIVE_PROFILE.format(
            install_dir=str(install_dir)
        )
        profile_path.write_text(profile_content)
        return profile_path
    except Exception as e:
        raise InstallError(f"Failed to create installation profile: {str(e)}")

def run_installer(installer_dir: Path, profile_path: Path) -> None:
    """
    Run the TeX Live installer.

    Parameters
    ----------
    installer_dir : Path
        Directory containing the installer
    profile_path : Path
        Path to the installation profile

    Raises
    ------
    InstallError
        If installation fails
    """
    logger.info("Running TeX Live installer (this may take a while)...")
    try:
        run_command(
            ["./install-tl", "-profile", profile_path],
            cwd=installer_dir,
            error_msg="TeX Live installation failed",
            capture_output=False  # Show real-time output during installation
        )
    except Exception as e:
        raise InstallError(f"TeX Live installation failed: {str(e)}")

def install_pandoc() -> None:
    """
    Install Pandoc using the system package manager.

    Raises
    ------
    InstallError
        If installation fails
    """
    logger.info("Installing Pandoc...")

    system = get_platform()
    try:
        if system == "darwin":  # macOS
            run_command(
                ["brew", "install", "pandoc"],
                error_msg="Failed to install Pandoc"
            )
        elif system == "linux":
            # Try apt first, then other package managers
            package_managers = [
                ["apt-get", "update", "&&", "apt-get", "install", "-y", "pandoc"],
                ["dnf", "install", "-y", "pandoc"],
                ["pacman", "-S", "--noconfirm", "pandoc"],
            ]

            for cmd in package_managers:
                try:
                    run_command(cmd, error_msg="Failed to install Pandoc")
                    break
                except InstallError:
                    continue
            else:
                raise InstallError("No supported package manager found")
        else:
            raise InstallError(f"Unsupported operating system: {system}")

    except Exception as e:
        raise InstallError(f"Failed to install Pandoc: {str(e)}")

def verify_installation() -> None:
    """
    Verify that all required components are installed and working.

    Raises
    ------
    DependencyError
        If any required component is missing
    """
    required_commands = [
        "pdflatex",       # Basic LaTeX compiler
        "tlmgr",          # TeX Live package manager
        "latexmk",        # Build automation
        "pandoc",         # Document conversion
        "bibtex"          # Bibliography processing
    ]
    missing = []

    for cmd in required_commands:
        if not check_command_exists(cmd):
            missing.append(cmd)

    if missing:
        raise DependencyError(
            f"Missing required commands: {', '.join(missing)}. "
            "Please ensure TeX Live and Pandoc are properly installed."
        )

def install_core_packages() -> None:
    """
    Install core LaTeX packages required for the project templates.

    Raises
    ------
    InstallError
        If package installation fails
    """
    core_packages = [
        # Math and symbols
        "amsmath",
        "amsthm",
        "amssymb",
        # Graphics and figures
        "graphics",
        "graphicx",
        "subfig",
        "float",
        "caption",
        "subcaption",
        # Tables
        "booktabs",
        "longtable",
        # URLs and references
        "url",
        "cite",
        "bibtex",
        # Special packages
        "tikz",
        "textgreek",
        "siunitx",
        # Core tools
        "latexmk",
        "texliveonfly"  # Automatically install missing packages
    ]

    logger.info("Installing core LaTeX packages...")
    try:
        run_command(
            ["tlmgr", "install"] + core_packages,
            error_msg="Failed to install core packages"
        )
    except Exception as e:
        raise InstallError(f"Failed to install core packages: {str(e)}")

def install_texlive() -> int:
    """
    Install TeX Live and required components.

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """
    try:
        if all(check_command_exists(cmd) for cmd in ["pdflatex", "tlmgr", "latexmk"]):
            logger.info("TeX Live appears to be already installed.")
            return 0

        install_dir = Path("/usr/local/texlive")
        if not check_write_permission(install_dir):
            raise InstallError(
                f"No write permission for {install_dir}. "
                "Please run with sudo or choose a different installation directory."
            )

        installer_path = download_texlive_installer()
        installer_dir = extract_installer(installer_path)

        profile_path = create_profile(install_dir)
        run_installer(installer_dir, profile_path)

        if not check_command_exists("pandoc"):
            install_pandoc()
        install_core_packages()
        verify_installation()

        logger.info("Installation completed successfully!")
        return 0

    except Exception as e:
        logger.error(str(e))
        return 1

    finally:
        if 'installer_path' in locals():
            installer_path.parent.unlink(missing_ok=True)

def update_texlive() -> int:
    """
    Update TeX Live and installed packages.

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """
    try:
        logger.info("Updating TeX Live...")
        run_command(
            ["tlmgr", "update", "--self", "--all"],
            error_msg="Failed to update TeX Live"
        )

        logger.info("TeX Live updated successfully!")
        return 0

    except Exception as e:
        logger.error(str(e))
        return 1
