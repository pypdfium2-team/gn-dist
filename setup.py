# SPDX-FileCopyrightText: 2026 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
import shlex
import subprocess
from pathlib import Path
import setuptools
from setuptools.command.build_py import build_py
try:
    from setuptools.command.bdist_wheel import bdist_wheel
except ImportError:
    from wheel.bdist_wheel import bdist_wheel

PROJECT_DIR = Path(__file__).parent
VERSION_FILE = Path(PROJECT_DIR/"src"/"gn_dist"/"VERSION")

sys.path.insert(0, str(PROJECT_DIR))
import build_gn  # local


def log(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)

def _run_cmd(cmd, **kwargs):
    log(cmd)
    return subprocess.run(cmd, **kwargs)

def infer_version():
    # let's avoid setuptools-scm (we like neither its high complexity nor the automatic file inclusion behavior)
    try:
        p = _run_cmd(["git", "describe", "--tags", "--dirty"], stdout=subprocess.PIPE, cwd=PROJECT_DIR, check=True)
        version = p.stdout.decode().strip()
        version = version.replace("-", "+", 1).replace("-", ".")
        VERSION_FILE.write_text(version)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        log(e)
        if not VERSION_FILE.exists():
            raise FileNotFoundError("If `git describe` is unavailable, a src/gn_dist/VERSION file must be provided. (Advice: If it's a shallow clone, either run `git fetch --unshallow`, or clone a tagged commit and run `git fetch --tags` to make `git describe` work.)")
        version = VERSION_FILE.read_text().strip()
    assert version, "Version must be non-empty"
    return version


class BuildPyClass(build_py):
    def run(self):
        argv = shlex.split( os.environ.get("BUILD_PARAMS", "") )
        build_gn.main(argv)
        super().run()

class BdistWheelClass(bdist_wheel):
    def get_tag(self, *args, **kws):
        _py, _abi, plat_tag = super().get_tag(*args, **kws)
        return "py3", "none", plat_tag

class BinaryDistribution (setuptools.Distribution):
    def has_ext_modules(self):
        return True


setuptools.setup(
    version = infer_version(),
    cmdclass = {"build_py": BuildPyClass, "bdist_wheel": BdistWheelClass},
    distclass = BinaryDistribution,
    # The following is required for compatibility with python 3.6 and its max setuptools version.
    # Note: Re-declaring `name` does not seem to conflict with pyproject.toml (if supported, pyproject.toml wins). This just avoids getting "UNKNOWN" as project name.
    name="gn-dist",
    package_dir = {"gn_dist": "src/gn_dist"},
    packages = setuptools.find_packages(where='src', include=["gn_dist*"]),
    # [project.scripts]
    entry_points = {"console_scripts": ["gn = gn_dist.__main__:main"]},
    # [tool.setuptools.package-data]
    package_data = {"gn_dist": ["gn"]},
)
