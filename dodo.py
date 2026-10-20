"""
doit task/build automation
"""

import os
import shutil
import subprocess
from pathlib import Path

from lattice import Lattice

# `doit` alone (and CI) builds the site; the PDF needs Chrome, so it runs only as `doit generate_pdf`.
DOIT_CONFIG = {"default_tasks": ["validate_example_files", "generate_web_docs"]}

# Lattice's default build_validation=True runs validate_example_files() eagerly at
# import time, so any known-broken example would crash `doit list` (or any other
# task) before doit's task graph even runs -- not just the validate_example_files
# task itself. Run every build_validation step except that last one here instead,
# and leave example validation to task_validate_example_files below, where a
# failure is an ordinary doit task failure rather than an import-time crash.
climate_data_model = Lattice(build_validation=False)
climate_data_model.generate_meta_schemas()
climate_data_model.validate_schemas()
climate_data_model.generate_json_schemas()


def task_validate_example_files():
    """Validates the example files against the JSON schema (and other validation steps)"""
    return {
        "file_dep": climate_data_model.examples
        + [schema.schema.file_path for schema in climate_data_model.schema_info],
        "actions": [(climate_data_model.validate_example_files, [])],
    }


def task_generate_web_docs():
    """Generates Markdown Documentation"""
    return {
        "file_dep": [schema.schema.file_path for schema in climate_data_model.schema_info]
        + [template.path for template in climate_data_model.doc_templates]
        # about.md, config.yaml, and extra-pages/ aren't templates, but the site is built from them too.
        + [path for path in Path("docs/web").rglob("*") if path.is_file()],
        "targets": [os.path.join(climate_data_model.web_docs_directory_path, "public")],
        "actions": [(climate_data_model.generate_web_documentation, [])],
    }


# Temporary stopgap until Lattice generates PDFs itself (bigladder/lattice#8): this prints
# the web site's combined print page with headless Chrome. Good enough for a committee review
# copy, but not publication quality (no page layout, numbered tables, or cross-references).
# Delete this block, and the DOIT_CONFIG above, once Lattice's own PDF output exists.
PRINT_PAGE_PATH = Path(climate_data_model.web_docs_directory_path, "public", "print_page", "index.html")
PDF_PATH = Path(climate_data_model.web_docs_directory_path, "ClimateInformation.pdf")
CHROME_NAMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser")
MACOS_CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def find_chrome():
    """Chrome or Chromium: $CHROME if set, else the usual names on PATH, else the macOS app."""
    if os.environ.get("CHROME"):
        return os.environ["CHROME"]
    for name in CHROME_NAMES:
        if shutil.which(name):
            return shutil.which(name)
    if Path(MACOS_CHROME_PATH).is_file():
        return MACOS_CHROME_PATH
    raise RuntimeError("Printing the PDF needs Chrome or Chromium; set $CHROME to its path.")


def print_pdf():
    """Print the site's combined print page (Lattice's `print_page` option) to PDF."""
    subprocess.run(
        [
            find_chrome(),
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            # Gives Mermaid time to draw the diagrams before the page is printed.
            "--virtual-time-budget=30000",
            f"--print-to-pdf={PDF_PATH.resolve()}",
            PRINT_PAGE_PATH.resolve().as_uri(),
        ],
        check=True,
    )


def task_generate_pdf():
    """Generates an interim PDF of the whole web site, for committee review (see stopgap note above)"""
    return {
        "task_dep": ["generate_web_docs"],
        "file_dep": [PRINT_PAGE_PATH],
        "targets": [PDF_PATH],
        "actions": [print_pdf],
    }
