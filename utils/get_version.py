# SPDX-FileCopyrightText: 2026 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: BSD-3-Clause

import re
from pathlib import Path

PROJECT_DIR = Path(__file__).parents[1].resolve()
pyproject_file = PROJECT_DIR/"pyproject.toml"

content = pyproject_file.read_text()
match = re.search(r'version = "([\w\.]+)"', content)
assert match
version = match.group(1)
print(version, end="")
