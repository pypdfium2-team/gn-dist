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

### Building

[`./build_gn.py`](build_gn.py) automates the build process (run with `--help` for options, as usual).

gn-dist's setup implies building GN. Run e.g. `pip install -v .` or `pyproject-build -wxn`.<br>
Set `$BUILD_PARAMS` to pass options to `build_gn.py` through the setup layer.

#### Versioning

gn-dist (and GN itself) use `git` to infer version info.

This is known to cause issues with shallow checkouts.
We recommend that you configure your clone of gn-dist in a way that allows `git describe` to do its job.

Where that is not possible (e.g. when installing from a tarball that does not contain the git repository) a `src/gn_dist/VERSION` file must be provided.<br>
This is just a plain text file containing the version string that will be passed to gn-dist's PEP 517 build backend.
The version should be provided as a [PEP 440 / PyPA specs](https://packaging.python.org/en/latest/specifications/version-specifiers/#version-specifiers) compatible normalization of what would otherwise be returned by `git describe`.<br>
The `VERSION` file is included in sdists and will be auto-generated where possible.

GN checkout is typically managed by gn-dist itself (which does a full clone), but if you insist on bringing your own copy of GN, you may need to provide a `//out/last_commit_position.h` file (relative to `//sbuild/gn`), in the following format:
```hpp
#ifndef OUT_LAST_COMMIT_POSITION_H_
#define OUT_LAST_COMMIT_POSITION_H_

#define LAST_COMMIT_POSITION_NUM %(num)s
#define LAST_COMMIT_POSITION "%(num)s (%(commit_id)s)"

#endif  // OUT_LAST_COMMIT_POSITION_H_
```
where `%(num)s` is the commit number (counted from the initial commit), and `%(commit_id)s` the commit hash (truncated to the first 12 digits), as in
```bash
git describe HEAD --abbrev=12 --match initial-commit
```
Then edit `build_gn.py` to pass `--no-last-commit-position` to GN's `build/gen.py`.

#### Containerization

To manually build gn-dist in a manylinux2014 container, you can do e.g.:

```bash
docker run -v "${PWD}:/projects/gn-dist" --security-opt label=disable -it quay.io/pypa/manylinux2014_x86_64 bash
```
```bash
# this would test python 3.6 compatibility - to use a contemporary version of python, comment in the lines below instead
yum install -y python3
#manylinux-interpreters ensure cp314-cp314
#export PATH="/opt/python/cp314-cp314/bin:${PATH}"
manylinux-install-clang -v latest
python3 -m venv /projects/.venv
export PATH="$/projects/.venv/bin:${PATH}"
python3 -m pip install -U pip
python3 -m pip install -U setuptools wheel build auditwheel
python3 -m pip install -U ninja  # scikit-build/ninja-python-distributions
cd /projects/gn-dist
./build_gn.py --help  # informational
BUILD_PARAMS="-c clang --clang-path /opt/clang" python3 -m build -wxn
#auditwheel repair dist/gn_dist-*.whl
```
<!-- TODO fix purelib vs. platlib issue with older python, then enable `auditwheel repair` above -->

### Updating (for maintainers)

To make a new release, first update the `GN_REV` in `build_gn.py` and rebuild locally.<br>
Commit and push the changes. Then run `src/gn_dist/gn --version` to determine the version, and create a matching tag (add a minor cipher if it's a rebuild):
```bash
git tag -a VERSION -m "Release"
```
Once you're positive, push the tag. For maintainer convenience, pushing a tag that points to the `HEAD` of `main` will automatically trigger the build workflow with publish options enabled.

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
