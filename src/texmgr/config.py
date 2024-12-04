"""Configuration and templates for texmgr."""

from pathlib import Path
from typing import Dict, List

# Project directory structure
PROJECT_DIRS = [
    "format",
    "text",
    "fig",
    "output/pdf",
    "output/word",
    "output/html",
    "output/logs",
]

# Default LaTeX packages that should be installed
DEFAULT_PACKAGES = [
    "amsmath",
    "amsthm",
    "graphicx",
    "subfig",
    "booktabs",
    "url",
    "float",
    "longtable",
    "caption",
    "subcaption",
    "tikz",
    "textgreek",
    "siunitx",
    "cite",
    "bibtex",
]

# LaTeX document templates
TEMPLATES = {
    "article": {
        "main.tex": """\\documentclass{article}
\\input{format/preamble}
\\input{format/title}

\\begin{document}
    \\maketitle
    \\tableofcontents
    \\newpage
    \\input{text/body}
    \\input{format/references}
\\end{document}
""",
        "format/packages.tex": """\\usepackage[cmex10]{amsmath}
\\usepackage{amsthm,amssymb}
\\usepackage[pdftex]{graphicx}
\\DeclareGraphicsExtensions{.pdf,.png,.jpg}
\\usepackage[caption=false]{subfig}
\\usepackage{booktabs}
\\usepackage{url}
\\urlstyle{same}
\\usepackage{amsmath}
\\usepackage{float}
\\usepackage{longtable}
\\usepackage{caption}
\\usepackage{subcaption}
\\usepackage{tikz}
\\usepackage{textgreek}
\\usepackage{siunitx}
\\usepackage{cite}
\\usepackage{bibtex}
""",
        "format/preamble.tex": """% Load packages
\\input{format/packages}

% Document settings
\\setlength{\\parindent}{0pt}
\\setlength{\\parskip}{1em}

% Custom commands and environments
""",
        "format/references.tex": """\\bibliographystyle{unsrt}
\\bibliography{refs}
""",
        "format/title.tex": """\\title{Document Title}
\\author{Author Name}
\\date{\\today}
""",
        "text/body.tex": """\\section{Introduction}
Your content here.
""",
        "refs.bib": """% Add your references here
""",
        ".gitignore": """# LaTeX
*.aux
*.bbl
*.blg
*.log
*.out
*.toc
*.synctex.gz
output/
"""
    },
    "beamer": {
        "main.tex": """\\documentclass{beamer}
\\input{format/preamble}
\\input{format/title}

\\begin{document}
    \\frame{\\titlepage}
    \\input{text/body}
    \\input{format/references}
\\end{document}
""",
        "format/packages.tex": """\\usepackage[cmex10]{amsmath}
\\usepackage{amsthm,amssymb}
\\usepackage[pdftex]{graphicx}
\\DeclareGraphicsExtensions{.pdf,.png,.jpg}
\\usepackage{booktabs}
\\usepackage{url}
\\urlstyle{same}
\\usepackage{amsmath}
""",
        "format/preamble.tex": """% Load packages
\\input{format/packages}

% Beamer theme settings
\\usetheme{Madrid}
\\usecolortheme{default}

% Custom commands and environments
""",
        "format/references.tex": """\\bibliographystyle{unsrt}
\\bibliography{refs}
""",
        "format/title.tex": """\\title{Presentation Title}
\\author{Author Name}
\\institute{Institution}
\\date{\\today}
""",
        "text/body.tex": """\\section{Introduction}

\\begin{frame}
\\frametitle{First Slide}
Your content here.
\\end{frame}
""",
        "refs.bib": """% Add your references here
""",
        ".gitignore": """# LaTeX
*.aux
*.bbl
*.blg
*.log
*.nav
*.out
*.snm
*.toc
*.synctex.gz
output/
"""
    }
}

# TeX Live installation profile template
TEXLIVE_PROFILE = """selected_scheme scheme-basic
TEXDIR {install_dir}
TEXMFCONFIG $TEXMFSYSCONFIG
TEXMFHOME $TEXMFLOCAL
TEXMFLOCAL {install_dir}/texmf-local
TEXMFSYSCONFIG {install_dir}/texmf-config
TEXMFSYSVAR {install_dir}/texmf-var
TEXMFVAR $TEXMFSYSVAR
binary_x86_64-linux 1
instopt_adjustpath 1
instopt_adjustrepo 1
instopt_letter 0
instopt_portable 0
instopt_write18_restricted 1
tlpdbopt_autobackup 1
tlpdbopt_backupdir tlpkg/backups
tlpdbopt_create_formats 1
tlpdbopt_generate_updmap 0
tlpdbopt_install_docfiles 1
tlpdbopt_install_srcfiles 1
tlpdbopt_post_code 1
tlpdbopt_sys_bin /usr/local/bin
tlpdbopt_sys_info /usr/local/share/info
tlpdbopt_sys_man /usr/local/share/man
"""

def get_template_files(doc_type: str) -> Dict[str, str]:
    """
    Get template files for a document type.

    Parameters
    ----------
    doc_type : str
        Type of document ('article' or 'beamer')

    Returns
    -------
    Dict[str, str]
        Dictionary mapping file paths to their content

    Raises
    ------
    ValueError
        If doc_type is not recognized
    """
    if doc_type not in TEMPLATES:
        raise ValueError(f"Unknown document type: {doc_type}")

    return TEMPLATES[doc_type]
