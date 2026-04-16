"""Removes all outputs and metadata in the Jupyter Notebook examples that
cause painful diffs during code contribution and review time.
"""

import sys
from pathlib import Path

import nbformat as nbf


def remove_extraneous(notebook_fn: str | Path):
    """Delete outputs and metadata from Jupyter Notebook files."""
    if isinstance(notebook_fn, str):
        notebook_fn = Path(notebook_fn)
    with notebook_fn.open("r", encoding="utf-8") as f:
        notebook = nbf.read(f, as_version=4)

    for cell in notebook["cells"]:
        if cell["cell_type"] in ["code", "markdown"]:
            cell["metadata"] = {}

    with notebook_fn.open("w", encoding="utf-8") as f:
        nbf.write(notebook, f)
        nbf.write("\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No files provided")
        sys.exit(1)
    for fn in sys.argv[1:]:
        if not fn.endswith(".ipynb"):
            print(f"Skipping non-notebook file: {fn}")
            continue
        remove_extraneous(fn)
