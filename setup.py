# SPDX-FileCopyrightText: 2026 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
import shlex
from pathlib import Path
import setuptools
from setuptools.command.build_py import build_py
try:
    from setuptools.command.bdist_wheel import bdist_wheel
except ImportError:
    from wheel.bdist_wheel import bdist_wheel

sys.path.insert(0, str(Path(__file__).parent))
from build_gn import parse_args, assisted_build  # local


class BuildPyClass(build_py):
    def run(self):
        build_params = os.environ.get("BUILD_PARAMS", "")
        args = parse_args(shlex.split(build_params))
        assisted_build(**vars(args))
        build_py.run(self)

class BdistWheelClass(bdist_wheel):
    def get_tag(self, *args, **kws):
        _py, _abi, plat_tag = bdist_wheel.get_tag(self, *args, **kws)
        return "py3", "none", plat_tag

class BinaryDistribution (setuptools.Distribution):
    def has_ext_modules(self):
        return True


setuptools.setup(
    cmdclass = {"build_py": BuildPyClass, "bdist_wheel": BdistWheelClass},
    distclass = BinaryDistribution,
)
