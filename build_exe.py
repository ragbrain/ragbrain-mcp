#!/usr/bin/env python3
"""Build standalone Windows executable for ragbrain-mcp."""

import subprocess
import sys


def main():
    """Build the executable using PyInstaller."""
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--name",
        "ragbrain-mcp",
        "--console",
        "--clean",
        "src/ragbrain_mcp/server.py",
    ]

    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print("\nBuild complete! Executable is in dist/ragbrain-mcp.exe")


if __name__ == "__main__":
    main()
