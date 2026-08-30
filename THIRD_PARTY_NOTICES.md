# Third-Party Notices and License Review

NumeriPlot is distributed under `GPL-3.0-only`, but it depends on third-party
software that remains under its own license. This document records the Phase 3
review performed on 2026-08-30 for the planned NumeriPlot 0.1.0 Public Beta.
It is not legal advice.

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

## Resolved transitive components observed during validation

The Phase 6 clean environment resolved the following runtime dependencies on
2026-08-30. These observations are not a complete dependency lock and must not
be treated as the final binary inventory.

| Component | Observed version | License |
| --- | ---: | --- |
| contourpy | 1.3.3 | BSD-3-Clause |
| cycler | 0.12.1 | BSD-3-Clause |
| fonttools | 4.63.0 | MIT, with additional notices for incorporated code |
| kiwisolver | 1.5.1 | BSD-3-Clause |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause |
| pyparsing | 3.3.2 | MIT |
| python-dateutil | 2.9.0.post0 | Apache-2.0 OR BSD-3-Clause |
| pytz | 2026.3.post1 | MIT |
| tzdata | 2026.3 | Apache-2.0 |
| et-xmlfile | 2.0.0 | MIT |
| six | 1.17.0 | MIT |

The audited NumPy and SciPy macOS wheels also declare OpenBLAS and LAPACK
notices, the GCC runtime under `GPL-3.0-with-GCC-exception`, and libquadmath
under `LGPL-2.1-or-later`. Whether each native library is present in the final
application must be established from the built `.app`, not inferred from the
installed wheel alone.

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

## Binary-distribution obligations and release gate

No public binary may be published until all items below are satisfied for the
actual clean release build:

1. Include NumeriPlot's complete, unmodified GPLv3 text (`LICENSE`) and this
   notice with the application and source distribution.
2. Include the complete LGPLv3 text for Qt together with the incorporated
   GPLv3 text. Do not impose terms that prohibit reverse engineering for
   debugging modifications to Qt.
3. Provide equivalent, durable access to the exact Corresponding Source for
   NumeriPlot and the GPL-covered PyQt6 version shipped in the binary. The
   source offered with a release must correspond to that binary, including the
   scripts needed to control its build.
4. Provide the complete corresponding Qt 6.10.2 library source, including any
   modifications, or a license-compliant written source offer. Preserve the
   user's ability to replace/relink the LGPL library and provide sufficient
   installation information to run the relinked result.
5. Generate a manifest from the final `.app` and inspect PyInstaller analysis,
   Qt frameworks/plugins, Python runtime files, native `.dylib` dependencies,
   fonts, image codecs, and package metadata. Copy every applicable upstream
   copyright notice, license text, and attribution into the release materials.
6. Reconcile the final Qt frameworks/plugins with Qt 6.10.2's official
   third-party-code records and SBOM. Do the same for the license files shipped
   inside the exact NumPy, SciPy, pandas, Matplotlib, Pillow, and Python build
   artifacts.
7. Record the exact Python and PyInstaller versions, dependency hashes, source
   locations, and any local modifications. Re-run this review whenever a
   dependency or build input changes.

The release ZIP is therefore blocked until the clean-build inventory and the
source/relinking package are verified. A source URL alone is not assumed to
satisfy every redistribution condition; the release process must preserve the
required license texts, notices, source availability, and installation rights.

## Trademarks and attribution

Third-party names are used only to identify dependencies. They do not imply
endorsement of NumeriPlot. Istanbul Technical University is the maintainer's
academic affiliation only and is not the software owner, publisher, sponsor,
or support provider.
