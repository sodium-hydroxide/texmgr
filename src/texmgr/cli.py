import argparse
from pathlib import Path
from typing import Optional

from .utils.logs import setup_logging

def create_parser() -> argparse.ArgumentParser:
    """
    Create and return the argument parser for texmgr.

    Returns
    -------
    argparse.ArgumentParser
        Configured argument parser for the application

    Notes
    -----
    Configures the following commands:
    - install : Install TeX Live and required tools
    - init : Initialize a new LaTeX project
    - pkg : Manage LaTeX packages
    - build : Build documents
    - cleanup : Clean output directories
    - update : Update TeX Live and installed packages
    """
    parser = argparse.ArgumentParser(
        prog="texmgr", description="LaTeX project manager and build tool"
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Install command
    install_parser = subparsers.add_parser(
        "install", help="Install TeX Live and required tools"
    )

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new LaTeX project")
    init_parser.add_argument(
        "--no-git", action="store_true", help="Don't initialize git repository"
    )
    init_parser.add_argument(
        "--type",
        choices=["article", "beamer"],
        default="article",
        help="Type of document to create",
    )

    # Package management commands
    pkg_parser = subparsers.add_parser("pkg", help="Manage LaTeX packages")
    pkg_subparsers = pkg_parser.add_subparsers(dest="pkg_command", required=True)

    # Add package
    pkg_add = pkg_subparsers.add_parser("add", help="Add packages to the project")
    pkg_add.add_argument("packages", nargs="+", help="Package names to add")

    # Install packages
    pkg_install = pkg_subparsers.add_parser(
        "install", help="Install packages from packages.tex"
    )

    # Build commands
    build_parser = subparsers.add_parser("build", help="Build documents")
    build_parser.add_argument(
        "format", choices=["pdf", "word", "html", "all"], help="Output format to build"
    )
    build_parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch for changes and rebuild (only for PDF)",
    )

    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean output directories")

    # Update command
    update_parser = subparsers.add_parser(
        "update", help="Update TeX Live and installed packages"
    )

    return parser


def parse_args():
    """
    Parse command line arguments.

    Returns
    -------
    argparse.Namespace
        Parsed command line arguments
    """
    parser = create_parser()
    return parser.parse_args()


def main() -> Optional[int]:
    """
    Main entry point for texmgr.

    Returns
    -------
    Optional[int]
        Exit code, where:
        - 0 indicates success
        - 1 indicates error
        - None indicates no action taken

    Notes
    -----
    Handles the following commands:
    - install : Install TeX Live and required tools
    - init : Initialize a new LaTeX project
    - pkg : Manage LaTeX packages
    - build : Build documents
    - cleanup : Clean output directories
    - update : Update TeX Live and installed packages

    All exceptions are caught and logged appropriately.
    """
    args = parse_args()
    logger = setup_logging(args.verbose)

    try:
        if args.command == "install":
            from .install import install_texlive

            return install_texlive()

        elif args.command == "init":
            from .init import init_project

            return init_project(not args.no_git, args.type)

        elif args.command == "pkg":
            from .pkg import handle_package_command

            return handle_package_command(args.pkg_command, args)

        elif args.command == "build":
            from .builder import build_document

            return build_document(args.format, watch=args.watch)

        elif args.command == "cleanup":
            from .builder import cleanup

            return cleanup()

        elif args.command == "update":
            from .install import update_texlive

            return update_texlive()

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        if args.verbose:
            logger.exception("Detailed traceback:")
        return 1

    return 0
