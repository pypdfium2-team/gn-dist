# SPDX-FileCopyrightText: 2026 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
import stat
import shutil
import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.resolve()
SBUILD_DIR = PROJECT_DIR/"sbuild"
GN_DIR = SBUILD_DIR/"gn"
GN_REV = "9ece3f5254c273cb46606a6571963f931c3b012d"

def log(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)

def run_cmd(command, cwd, **kwargs):
    log(f"{command} (cwd={cwd})")
    return subprocess.run(command, cwd=cwd, check=True, **kwargs)

def make_executable(path):
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

def build_gn():
    # GN's build system runs git commands that assume a full checkout
    # --depth 1 checkout would need a manually created sbuild/gn/out/last_commit_position.h and passing "--no-last-commit-position" to build/gen.py - probably not worth the trouble for now.
    SBUILD_DIR.mkdir(exist_ok=True)
    if not GN_DIR.exists():
        run_cmd(["git", "clone", "https://gn.googlesource.com/gn/"], cwd=SBUILD_DIR)
        run_cmd(["git", "checkout", GN_REV], cwd=GN_DIR)
    env = os.environ.copy()
    env["CXX"] = os.environ.get("CXX", "g++")
    run_cmd([sys.executable, "build/gen.py", "--no-static-libstdc++", "--allow-warnings"], cwd=GN_DIR, env=env)
    run_cmd(["ninja", "-C", "out", "gn"], cwd=GN_DIR)
    target_path = PROJECT_DIR/"src"/"gn_dist"/"gn"
    shutil.copyfile(GN_DIR/"out"/"gn", target_path)
    make_executable(target_path)

if __name__ == "__main__":
    build_gn()
