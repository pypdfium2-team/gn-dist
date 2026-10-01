# SPDX-FileCopyrightText: 2026 geisserml <geisserml@gmail.com>
# SPDX-License-Identifier: BSD-3-Clause

list:
    just -l

build *args:
    python3 build_gn.py {{args}}

sync-locks:
    # assuming pypdfium2 and gn-dist share the same parent directory
    cp ../pypdfium2/lock/distcheck.txt lock/distcheck.txt
update-actions $MIN_AGE='7':
	pinact run -update -min-age "$MIN_AGE" || true
update-all-pins: sync-locks update-actions

zizmor *args:
	zizmor .github/ --persona auditor {{args}}
