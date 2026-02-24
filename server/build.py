"""
Build script: runs PyInstaller with build.spec to create AppStore.exe.

Usage: From project root, run: python server/build.py

Output: dist/AppStore.exe
"""

import os
import subprocess
import sys

def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    spec_file = os.path.join(this_dir, "build.spec")
    # Run from project root so SPEC_DIR = getcwd() is correct
    project_root = os.path.dirname(this_dir)
    exe_path = os.path.join(project_root, "server", "dist", "AppStore.exe")
    if os.path.isfile(exe_path):
        try:
            with open(exe_path, "r+b"):
                pass
        except PermissionError:
            print("ERROR: AppStore.exe is in use (or locked). Close it and try again.")
            sys.exit(1)
    result = subprocess.run(
        [
            sys.executable, "-m", "PyInstaller", spec_file,
            "--distpath", os.path.join(project_root, "server", "dist"),
            "--workpath", os.path.join(project_root, "server", "build"),
        ],
        cwd=project_root,
        check=False,
    )
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
