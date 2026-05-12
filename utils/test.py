# SPDX-FileCopyrightText: 2026 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: BSD-3-Clause

import gn_dist
import subprocess

p = subprocess.run([str(gn_dist.GN), "--version"], check=True, capture_output=True)
print(p.stdout.decode().strip())
