"""Build script for ComicManager Neo.

Usage:
    uv run python build.py            # Full build (frontend + PyInstaller)
    uv run python build.py --dev      # Frontend build only (no PyInstaller)
    uv run python build.py --clean    # Clean build artifacts before building
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path.cwd()
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"


def _find_bun() -> str:
    """Locate bun executable."""
    bun = shutil.which("bun")
    if bun:
        return bun
    # Common Windows install location
    fallback = Path.home() / ".bun" / "bin" / "bun.exe"
    if fallback.exists():
        return str(fallback)
    print("ERROR: bun not found. Install from https://bun.sh or add to PATH.")
    sys.exit(1)


def clean():
    """Remove build artifacts."""
    for d in [DIST_DIR, BUILD_DIR]:
        if d.exists():
            print(f"Cleaning {d}...")
            shutil.rmtree(d, ignore_errors=True)


def build_frontend():
    """Build the Vue 3 frontend with bun."""
    print("Building frontend...")
    bun = _find_bun()
    old_cwd = Path.cwd()
    try:
        os.chdir(str(FRONTEND_DIR))
        subprocess.run([bun, "run", "build"], check=True)
    except subprocess.CalledProcessError:
        print("Frontend build failed!")
        sys.exit(1)
    finally:
        os.chdir(str(old_cwd))
    print("Frontend build complete.")


def build_executable():
    """Build the PyInstaller executable."""
    print("Building executable with PyInstaller...")

    # Ensure pyinstaller is importable
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("Installing pyinstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    result = subprocess.run(
        [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            str(PROJECT_ROOT / "comicmanager_neo.spec"),
        ],
        cwd=str(PROJECT_ROOT),
    )
    if result.returncode != 0:
        print("PyInstaller build failed!")
        sys.exit(1)
    print("Executable build complete.")


def main():
    parser = argparse.ArgumentParser(description="Build ComicManager Neo")
    parser.add_argument("--dev", action="store_true", help="Frontend only, skip PyInstaller")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts before building")
    args = parser.parse_args()

    if args.clean:
        clean()

    build_frontend()

    if not args.dev:
        build_executable()

    print("\nBuild complete!")
    if args.dev:
        print("Dev build: frontend/dist/ is ready.")
    else:
        exe_path = DIST_DIR / "ComicManagerNeo" / "ComicManagerNeo.exe"
        print(f"Executable: {exe_path}")


if __name__ == "__main__":
    main()
