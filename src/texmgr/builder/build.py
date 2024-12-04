"""Document build functionality using latexmk."""

from pathlib import Path
from typing import Optional

from ..utils.errors import BuildError
from ..utils.logs import logger
from ..utils.cmds import run_command, check_command_exists
from ..utils.fileops import ensure_dir, detect_project_root

def build_pdf(watch: bool = False) -> None:
    """
    Build PDF using latexmk.

    Parameters
    ----------
    watch : bool, optional
        Enable watch mode for automatic rebuilds, by default False

    Raises
    ------
    BuildError
        If build fails or project structure is invalid
    """
    if not check_command_exists("latexmk"):
        raise BuildError("latexmk not found. Please ensure it's installed.")

    project_root = detect_project_root()
    if not project_root:
        raise BuildError("Not in a LaTeX project directory")

    # Create output directory if it doesn't exist
    output_dir = project_root / "output" / "pdf"
    ensure_dir(output_dir)

    # Ensure both output directories exist
    output_dir = project_root / "output" / "pdf"
    aux_dir = project_root / "output" / "logs"
    ensure_dir(output_dir)
    ensure_dir(aux_dir)

    # Base latexmk command
    cmd = [
        "latexmk",
        "-pdf",                    # Generate PDF output
        "-interaction=nonstopmode",  # Don't stop for errors
        f"-output-directory={output_dir}",  # PDF output directory
        f"-aux-directory={aux_dir}",   # Auxiliary files directory
        "main.tex"                # Main tex file
    ]

    if watch:
        cmd.extend([
            "-pvc",               # Preview continuously (watch mode)
            "-view=none"          # Don't launch viewer
        ])

    try:
        logger.info("Building PDF...")
        run_command(
            cmd,
            cwd=project_root,
            error_msg="PDF build failed",
            capture_output=not watch  # Show output in real-time for watch mode
        )
        if not watch:
            logger.info(f"PDF built successfully: {output_dir}/main.pdf")
    except Exception as e:
        raise BuildError(f"Failed to build PDF: {str(e)}")

def build_word() -> None:
    """
    Convert LaTeX to Word using pandoc.

    Raises
    ------
    BuildError
        If conversion fails or project structure is invalid
    """
    if not check_command_exists("pandoc"):
        raise BuildError("pandoc not found. Please ensure it's installed.")

    project_root = detect_project_root()
    if not project_root:
        raise BuildError("Not in a LaTeX project directory")

    # Create output directory if it doesn't exist
    output_dir = project_root / "output" / "word"
    ensure_dir(output_dir)

    try:
        logger.info("Converting to Word...")
        run_command(
            [
                "pandoc",
                "main.tex",
                "-o", output_dir / "main.docx",
                "--resource-path", ".",
                "--reference-doc", "format/template.docx" if (project_root / "format/template.docx").exists() else None
            ],
            cwd=project_root,
            error_msg="Word conversion failed"
        )
        logger.info(f"Word document created: {output_dir}/main.docx")
    except Exception as e:
        raise BuildError(f"Failed to convert to Word: {str(e)}")

def build_html() -> None:
    """
    Convert LaTeX to HTML using pandoc.

    Raises
    ------
    BuildError
        If conversion fails or project structure is invalid
    """
    if not check_command_exists("pandoc"):
        raise BuildError("pandoc not found. Please ensure it's installed.")

    project_root = detect_project_root()
    if not project_root:
        raise BuildError("Not in a LaTeX project directory")

    # Create output directory if it doesn't exist
    output_dir = project_root / "output" / "html"
    ensure_dir(output_dir)

    try:
        logger.info("Converting to HTML...")
        run_command(
            [
                "pandoc",
                "main.tex",
                "-o", output_dir / "index.html",
                "--standalone",
                "--mathjax",
                "--resource-path", ".",
                "--css", "format/style.css" if (project_root / "format/style.css").exists() else None
            ],
            cwd=project_root,
            error_msg="HTML conversion failed"
        )
        logger.info(f"HTML document created: {output_dir}/index.html")
    except Exception as e:
        raise BuildError(f"Failed to convert to HTML: {str(e)}")

def build_document(format: str, watch: bool = False) -> int:
    """
    Build document in specified format.

    Parameters
    ----------
    format : str
        Output format ('pdf', 'word', 'html', or 'all')
    watch : bool, optional
        Enable watch mode for PDF builds, by default False

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """
    try:
        if format == "pdf" or format == "all":
            build_pdf(watch)
            if watch:  # Don't continue with other formats in watch mode
                return 0

        if format == "word" or format == "all":
            build_word()

        if format == "html" or format == "all":
            build_html()

        return 0

    except Exception as e:
        logger.error(str(e))
        return 1

def cleanup() -> int:
    """
    Clean up build artifacts.

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """
    try:
        project_root = detect_project_root()
        if not project_root:
            raise BuildError("Not in a LaTeX project directory")

        logger.info("Cleaning build artifacts...")

        # Run latexmk clean
        run_command(
            ["latexmk", "-c"],
            cwd=project_root,
            error_msg="Cleanup failed"
        )

        # Remove output files
        output_dir = project_root / "output"
        if output_dir.exists():
            for fmt_dir in ["pdf", "word", "html"]:
                fmt_path = output_dir / fmt_dir
                if fmt_path.exists():
                    for file in fmt_path.iterdir():
                        if file.is_file():
                            file.unlink()
                            logger.debug(f"Removed {file}")

        logger.info("Cleanup complete")
        return 0

    except Exception as e:
        logger.error(str(e))
        return 1
