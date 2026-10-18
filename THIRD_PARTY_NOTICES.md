# Third-Party Notices and License Review

NumeriPlot is distributed under `GPL-3.0-only`, but it depends on third-party
software that remains under its own license. This document records the review
first performed on 2026-08-30 and updated on 2026-10-18 for the NumeriPlot
0.2.0 macOS app. It is not legal advice.

## Declared runtime components

The following versions are pinned directly in `requirements.txt`.

| Component | Version | License reviewed | Official source/license |
| --- | ---: | --- | --- |
| PyQt6 | 6.10.2 | GPL-3.0-only | [Riverbank PyQt licensing](https://www.riverbankcomputing.com/software/pyqt/) · [release files](https://pypi.org/project/PyQt6/6.10.2/#files) |
| Qt supplied by PyQt6-Qt6 | 6.10.2 | LGPL-3.0-only for the supplied wheel; individual Qt modules and bundled code may carry additional compatible terms | [Qt licensing](https://doc.qt.io/qt-6/licensing.html) · [Qt 6.10.2 source](https://download.qt.io/official_releases/qt/6.10/6.10.2/single/) |
| PyQt6-sip | 13.11.0 | BSD-2-Clause | [release files](https://pypi.org/project/PyQt6-sip/13.11.0/#files) |
| Matplotlib | 3.10.1 | Matplotlib License (PSF-based) | [versioned license](https://github.com/matplotlib/matplotlib/blob/v3.10.1/LICENSE/LICENSE) |
| pandas | 2.2.3 | BSD-3-Clause, with additional notices for incorporated code | [versioned license](https://github.com/pandas-dev/pandas/blob/v2.2.3/LICENSE) |
| NumPy | 2.2.4 | BSD-3-Clause, with additional notices for incorporated and wheel-bundled code | [versioned license](https://github.com/numpy/numpy/blob/v2.2.4/LICENSE.txt) |
| SciPy | 1.15.2 | BSD-3-Clause, with additional notices for incorporated and wheel-bundled code | [versioned license](https://github.com/scipy/scipy/blob/v1.15.2/LICENSE.txt) |
| openpyxl | 3.1.5 | MIT | [project documentation](https://openpyxl.readthedocs.io/en/3.1/) · [release files](https://pypi.org/project/openpyxl/3.1.5/#files) |
| Pillow | 10.4.0 | HPND | [versioned license](https://github.com/python-pillow/Pillow/blob/10.4.0/LICENSE) |

The application is built with Python. The source tree currently requires
Python 3.11 or newer; the Phase 3 audit host used Python 3.11.1. The exact
Python patch version used for the release binary must be recorded during the
clean build. Python is distributed under the PSF License Agreement and related
incorporated-software licenses; see the
[official Python 3.11 license documentation](https://docs.python.org/3.11/license.html).

## Resolved transitive components

The 0.2.0 build environment resolved the following runtime dependencies. They
are not pinned; the notice index inside each app
(`licenses/third-party/INDEX.md`) lists the exact versions it bundles.

| Component | Version in the 0.2.0 build | License |
| --- | ---: | --- |
| contourpy | 1.3.3 | BSD-3-Clause |
| cycler | 0.12.1 | BSD-3-Clause |
| fonttools | 4.67.0 | MIT, with additional notices for incorporated code |
| kiwisolver | 1.5.1 | BSD-3-Clause |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause |
| pyparsing | 3.3.3 | MIT |
| python-dateutil | 2.9.0.post0 | Apache-2.0 OR BSD-3-Clause |
| pytz | 2026.5 | MIT |
| tzdata | 2026.5 | Apache-2.0 |
| et-xmlfile | 2.0.0 | MIT |
| six | 1.17.0 | MIT |

The NumPy, SciPy, pandas and Pillow wheels carry notices for the code and
native libraries they bundle. SciPy's macOS wheel includes OpenBLAS and the GCC
runtime libraries: libgfortran and libgcc_s under
`GPL-3.0-with-GCC-exception`, and libquadmath under `LGPL-2.1-or-later`.
Matplotlib's wheel omits the notices for its bundled fonts, color maps and Qt
figure editor; they are kept in `licenses/matplotlib-3.10.1/` from its source
distribution.

## Packaging tools

Development and packaging tools are separated from runtime requirements. The
clean Phase 6 build used the pinned PyInstaller 6.22.2, PyInstaller hooks
contrib 2026.7, altgraph 0.17.5, and macholib 1.16.4 declared in
`requirements-dev.txt`. PyInstaller is a build tool rather than a runtime API.
Its bootloader and build machinery are licensed under the terms and special
exception in its
[versioned `COPYING.txt`](https://github.com/pyinstaller/pyinstaller/blob/v6.22.2/COPYING.txt).
The build now stops if PyInstaller is absent instead of downloading tooling
during the release build.

## The macOS app

The disk image contains a self-contained `NumeriPlot.app` built with
PyInstaller on Apple Silicon. It bundles the runtime components above, the
Python 3.11.1 runtime, PyInstaller's bootloader and run-time hooks, and the
native libraries shipped inside those wheels. The components are unmodified
apart from the library paths and ad-hoc signatures that PyInstaller sets.

Of Qt, the app keeps QtCore, QtGui, QtDBus (which QtGui requires), QtWidgets
and QtSvg, with their platform, style, icon and image-format plugins from the
qtbase and qtsvg modules. QtPdf, QtNetwork, and the plugins that need them or
come from qtimageformats are left out because NumeriPlot never loads them
(`tools/bundle_policy.py`).

### What each release provides

1. **License texts and notices inside the app** (`Contents/Resources/licenses`,
   shown under **File → About NumeriPlot → Third-Party Licenses**): NumeriPlot's
   GPLv3 `LICENSE`, this document, the LGPLv3 text, the license files shipped
   with every bundled distribution, Python's license, PyInstaller's terms, and
   the third-party attributions for the bundled Qt modules
   (`licenses/Qt-6.10.2-third-party.txt`, generated by
   `tools/qt_attributions.py`). `tools/collect_licenses.py` gathers them for
   each build. The About dialog shows Qt's notice next to NumeriPlot's, and the
   disk image carries a short bilingual notice.
2. **Source code next to the disk image** on the GitHub release:
   - NumeriPlot: the release's source archives, including `build_macos.sh`,
     `NumeriPlot.spec` and `tools/`, which control the build;
   - Qt 6.10.2: `qtbase-everywhere-src-6.10.2.tar.xz` and
     `qtsvg-everywhere-src-6.10.2.tar.xz`;
   - PyQt6 6.10.2: `pyqt6-6.10.2.tar.gz`;
   - GCC runtime: `gcc-12.1.0.tar.xz`.

   `tools/fetch_release_sources.py` downloads these official archives and
   verifies them against pinned checksums taken from Qt's `.sha256` files,
   GCC's `sha512.sum` and PyPI.
3. **The right to replace Qt**, described below. NumeriPlot's terms do not
   restrict reverse engineering for debugging such modifications.

### Replacing Qt

The Qt frameworks and plugins are separate files inside
`NumeriPlot.app/Contents/Frameworks/PyQt6/Qt6/` (`lib/` and `plugins/`). To use
a modified Qt, build a binary-compatible Qt 6.10 for arm64 macOS from the
source archives, copy your frameworks or plugins over the bundled ones, and
re-sign the app locally:

```bash
codesign --force --deep --sign - NumeriPlot.app
```

### GCC runtime source

SciPy 1.15.2's wheel contains these libraries as built by the
[gfortran-for-macOS 12.1](https://github.com/fxcoudert/gfortran-for-macOS)
toolchain, which applies the Darwin/arm64 port maintained in
[iains/gcc-12-branch](https://github.com/iains/gcc-12-branch) on top of
GCC 12.1. That toolchain release does not identify an exact source commit, and
SciPy's own license file names the GCC sources as the origin of these
libraries. NumeriPlot follows SciPy's practice: it ships SciPy's notices
unmodified and publishes the GCC 12.1.0 release archive together with the link
to the Darwin branch. The maintainer adopted this standard on 2026-10-18.

### Release checklist

Before publishing an app release, the maintainer confirms that:

1. `bash release_check.sh` passes and `bash build_macos.sh` completes, including
   its SciPy wheel check, notice collection, `tools/check_app_bundle.py`, and
   the signature and disk-image verification;
2. `python3 tools/fetch_release_sources.py` completes, and its archives,
   `SHA256SUMS` and `README.txt` are uploaded together with the disk image and
   its `.sha256` file;
3. the app installed from the disk image opens on a real Mac, loads the example
   project, and exports a figure; and
4. this document, `requirements*.txt`, `licenses/Qt-*-third-party.txt` and
   `licenses/<package>-<version>/` are updated together whenever a bundled
   dependency, Python or PyInstaller changes. The build stops when the Qt or
   Matplotlib notices no longer match the installed versions.

## Trademarks and attribution

Third-party names are used only to identify dependencies. They do not imply
endorsement of NumeriPlot. Istanbul Technical University is the maintainer's
academic affiliation only and is not the software owner, publisher, sponsor,
or support provider.
