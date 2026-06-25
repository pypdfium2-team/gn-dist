# SPDX-FileCopyrightText: 2026 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
import stat
import shutil
import argparse
import subprocess
from pathlib import Path
from collections import namedtuple

PROJECT_DIR = Path(__file__).parent.resolve()
SBUILD_DIR = PROJECT_DIR/"sbuild"
GN_DIR = SBUILD_DIR/"gn"
GN_REV = "3357c4f51b1a9e676378c695dd9c7e9911c35ee6"


def log(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)

def run_cmd(command, cwd, **kwargs):
    log(f"{command} (cwd={cwd})")
    return subprocess.run(command, cwd=cwd, check=True, **kwargs)

def env_prepend(key, value, sep):
    tail = os.environ.get(key, "")
    if tail:
        tail = sep + tail
    os.environ[key] = value + tail

def _make_executable(path):
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def build(env=None):
    
    # GN's build system runs git commands that assume a full checkout
    # --depth 1 checkout would need a manually created sbuild/gn/out/last_commit_position.h and passing "--no-last-commit-position" to build/gen.py - probably not worth the trouble for now.
    SBUILD_DIR.mkdir(exist_ok=True)
    if not GN_DIR.exists():
        run_cmd(["git", "clone", "https://gn.googlesource.com/gn/"], cwd=SBUILD_DIR)
        run_cmd(["git", "checkout", GN_REV], cwd=GN_DIR)
    
    args = [sys.executable, "build/gen.py", "--allow-warnings", "--no-static-libstdc++"]
    run_cmd(args, cwd=GN_DIR, env=env)
    # TODO on CI, build and run unittests
    run_cmd(["ninja", "-C", "out", "gn"], cwd=GN_DIR)
    target_path = PROJECT_DIR/"src"/"gn_dist"/"gn"
    shutil.copyfile(GN_DIR/"out"/"gn", target_path)
    _make_executable(target_path)


CompilerToolset = namedtuple("CompilerToolset", ("CXX", "AR", "LD"), defaults=(None, ))

def assisted_build(compiler=None, toolprefix="", clang_path=None):
    
    if compiler is None:
        if shutil.which("g++"):
            compiler = "gcc"
        elif shutil.which("clang++"):
            compiler = "clang"
        else:
            raise RuntimeError("A compiler is needed, but neither g++ nor clang++ were found")
    
    if compiler == "gcc":
        toolset = CompilerToolset(CXX=toolprefix+"g++", AR=toolprefix+"ar")
    elif compiler == "clang":
        toolset = CompilerToolset(CXX="clang++", AR="llvm-ar")
        if clang_path:
            env_prepend("PATH", str(clang_path/"bin"), os.pathsep)
    elif compiler == "custom":
        toolset = CompilerToolset(
            CXX=os.environ["CXX"], AR=os.environ["AR"], LD=os.environ.get("LD"),
        )
    else:
        assert False, compiler
    
    env = os.environ.copy()
    env["CXX"] = toolset.CXX
    env["AR"] = toolset.AR
    env["LD"] = toolset.LD or toolset.CXX
    
    build(env)


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="GN build script",
    )
    parser.add_argument(
        "-c", "--compiler",
        choices=("gcc", "clang", "custom"),
        help = "The compiler to use.",
    )
    parser.add_argument(
        "--toolprefix",
        default = "",
        help = "(gcc only) Toolprefix to use.",
    )
    parser.add_argument(
        "--clang-path",
        type = lambda p: Path(p).expanduser().resolve(),
        help = "(clang only) Clang root dir to use.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    args = parse_args(argv)
    assisted_build(**vars(args))


if __name__ == "__main__":
    main()
