from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = ROOT / ".venv-data"
REQUIREMENTS = ROOT / "requirements-data.txt"
EXPORTER = ROOT / "scripts" / "export_dashboard_snapshot.py"


def venv_python_path() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def run(command: list[str]) -> None:
    subprocess.run(command, check=True, cwd=str(ROOT))


def ensure_venv() -> Path:
    python_bin = venv_python_path()
    if python_bin.exists():
        return python_bin
    run([sys.executable, "-m", "venv", str(VENV_DIR)])
    return python_bin


def main() -> None:
    python_bin = ensure_venv()
    run([str(python_bin), "-m", "pip", "install", "-r", str(REQUIREMENTS)])
    run([str(python_bin), str(EXPORTER)])


if __name__ == "__main__":
    main()
