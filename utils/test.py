# SPDX-FileCopyrightText: 2026 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: BSD-3-Clause

import gn_dist
from subprocess import check_output

out = check_output([str(gn_dist.GN), "--version"])
print(out.decode().strip())
