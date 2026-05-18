"""Ensure repository root is on sys.path when Streamlit runs an entry under app/frontend/."""
from pathlib import Path
import sys


def ensure_repo_root() -> str:
    root = str(Path(__file__).resolve().parent.parent.parent)
    if root not in sys.path:
        sys.path.insert(0, root)
    return root
