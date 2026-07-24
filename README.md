<!-- SPDX-FileCopyrightText: 2026 geisserml <geisserml@gmail.com> -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# gn-dist

Binary distributions of [GN][] (generate-ninja) for Linux (glibc and musl).

Other systems are out of scope for this project. For Windows and macOS builds, please refer to [Google CIPD][].

[GN]: https://gn.googlesource.com/gn
[Google CIPD]: https://chrome-infra-packages.appspot.com/p/gn/gn

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

### Updating (for maintainers)

To make a new release, first update the `GN_REV` in `build_gn.py` and rebuild locally.<br>
Commit the changes. Then run `src/gn_dist/gn --version` to determine the version, and create a matching tag (add a minor cipher if it's a rebuild):
```bash
git tag -a VERSION -m "Release"
```
Push commit and tag. Finally, go to the Actions panel and run `Build` with the `publish` and `actually_publish` options checked.

Once a release has been successfully published to GitHub, tag protection from immutable releases will lock the tag in place.
However, if anything goes wrong before that, you may just revoke the tag as usual:
```bash
git tag -d VERSION
git push --delete origin VERSION
```
Then you can fix things up and eventually re-create the tag on another commit.

### History

See below for some background why `gn-dist` was created:
- https://groups.google.com/g/pdfium/c/1__HW-wzJ8c/m/5MCYXAuDBQAJ
- https://chromium-review.googlesource.com/c/chromium/src/+/7593779/comments/fdd2633a_eb123349
- https://gn.googlesource.com/gn/+/88604adbcec2101f25b2e3ebd7f39b38163a6a33/README.md#versioning-and-distribution

### Related work

If you are looking for PyPI builds of `ninja`,
[`scikit-build/ninja-python-distributions`](https://github.com/scikit-build/ninja-python-distributions)
is somewhat equivalent to this project.
Note though, it uses Kitware's fork of ninja, not the original version.

There is also [`loong64/gn`](https://github.com/loong64/gn), but for some reason refers to a little-known fork of GN, is not regularly updated, does not include musllinux builds, and is not Python packaged.
