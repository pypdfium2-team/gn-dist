<!-- SPDX-FileCopyrightText: 2026 geisserml <geisserml@gmail.com> -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# gn-dist

Binary distributions of GN (generate-ninja) for Linux (glibc and musl).

### Installation
```bash
python3 -m pip install gn-dist

# convenience wrapper script
GN_WRAPPER=$(which gn)
$GN_WRAPPER --version

# actual binary
GN_EXE=$(python3 -c "from gn_dist import GN; print(str(GN))")
$GN_EXE --version

# to add the actual binary to PATH, you can do e.g.:
GN_DIR="$(dirname $GN_EXE)"  # or use GN.parent above
export PATH="$GN_DIR:$PATH"
# ^ add this to your ~/.bashrc if you want
```

For Windows and macOS, you'll want Google's builds from CIPD:<br/>
https://chrome-infra-packages.appspot.com/p/gn/gn

### Updating

To make a new release, first update the `GN_REV` in `build_gn.py` and rebuild locally.

Then run `src/gn_dist/gn --version` and manually update the `version` field in `pyproject.toml`.<br/>
Also, you may want to update the cibuildwheel pin in `build_one.yaml`, and the clang pin in `pyproject.toml`.

Commit and push the changes. Finally, go to the Actions panel and run `Build` with the `publish` option checked.

### History

See below for some background why `gn-dist` was created:
- https://groups.google.com/g/pdfium/c/1__HW-wzJ8c/m/5MCYXAuDBQAJ
- https://chromium-review.googlesource.com/c/chromium/src/+/7593779/comments/fdd2633a_eb123349

### Related work

If you are looking for PyPI builds of `ninja`,
[`scikit-build/ninja-python-distributions`](https://github.com/scikit-build/ninja-python-distributions)
is somewhat equivalent to this project.
Note though, it uses Kitware's fork of ninja, not the original version.
