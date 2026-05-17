# SPDX-FileCopyrightText: 2026 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: BSD-3-Clause

import sys
import subprocess
from gn_dist import GN

def main():
    p = subprocess.run([str(GN), *sys.argv[1:]])
    sys.exit(p.returncode)

if __name__ == "__main__":
    main()
