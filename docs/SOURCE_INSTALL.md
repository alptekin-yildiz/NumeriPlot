# Install and use NumeriPlot from source on a Mac

[Türkçe](SOURCE_INSTALL_TR.md) · [User guide](https://alptekin-yildiz.github.io/NumeriPlot/en.html)

The distribution route for 0.1.1 is source code; no prebuilt Mac application
ZIP is planned. NumeriPlot opens as a normal desktop window with plots and
tables. You do not need to write code or build an `.app` to use it. Initial
setup takes a few Terminal commands; subsequent launches are shorter.

## 1. Requirements

- Internet access for the initial dependency installation and updates.
- Python **3.11**, the Python series used in local application tests. Newer
  Python versions have not been validated here with the pinned dependencies.
- Apple Silicon Mac: the local check used macOS 27.0.1 and Python 3.11.1.
  Equivalent validation has not been performed on Intel, Windows, Linux, or
  older macOS versions. The previous package's “macOS 12+” description does
  not establish support for this installation route.

Open **Terminal** using Spotlight. This command only displays the Python
version and does not change your computer:

```bash
python3.11 --version
```

If Python 3.11 is missing and you use Homebrew, the following command downloads
and installs it with its required components:

```bash
brew install python@3.11
```

If Homebrew is missing, follow its [official installation instructions](https://docs.brew.sh/Installation)
and complete the final PATH steps shown by the installer. Homebrew's system
requirements are separate from NumeriPlot's; check support for your Mac.
An existing working Python 3.11 from another provider does not require
Homebrew. Do not remove or modify Apple's system Python.

## 2. Download the source

1. Open the [NumeriPlot repository](https://github.com/alptekin-yildiz/NumeriPlot).
2. On the [0.1.1 release page](https://github.com/alptekin-yildiz/NumeriPlot/releases/tag/v0.1.1),
   choose **Assets → Source code (zip)**. This is source code, not a prebuilt
   application. **Code → Download ZIP** on the repository downloads the moving
   `main` branch; prefer the 0.1.1 archive for this guide.
3. Extract the archive and move the folder to a permanent location. It must
   contain `main.py`, `setup.sh`, and `requirements.txt`.
4. Type `cd` followed by a space in Terminal, drag that folder from Finder
   into Terminal, then press Return. This changes Terminal's working folder;
   it does not move the folder. Run the following commands from there.

Users familiar with Git can instead clone the repository:

```bash
git clone https://github.com/alptekin-yildiz/NumeriPlot.git
cd NumeriPlot
```

## 3. Set up once

Run these commands **one at a time** in the newly downloaded folder. If one
fails, consult troubleshooting before proceeding.

The first creates the project's `venv` environment; the second activates it.
The third downloads dependencies at the versions in `requirements.txt`.
NumeriPlot's dependencies are installed into this folder, not system Python.

```bash
python3.11 -m venv venv
source venv/bin/activate
bash setup.sh
```

Then launch the application:

```bash
python3 main.py
```

Keep Terminal open while the app runs. Use the normal menus, file dialogs,
and mouse once it opens. Setup is not needed at every launch. Everyday use
does not require `--dev`, test tools, or PyInstaller.

## 4. Double-click to open on later days

In Finder, open the NumeriPlot source folder and double-click
**`NumeriPlot.command`**. A Terminal window opens, followed by the desktop
interface. Keep Terminal open while using the app; after quitting the app,
you can close that window. Installation does not run again on every launch.

Keep the launcher inside the project folder. For easy access, select it in
Finder, choose **File → Make Alias**, and move the alias to your desktop.

If setup is missing, the launcher shows where to find this guide. If the file
cannot open because it lacks execution permission, run this once in the
project folder; it only grants execution permission to the launcher:

```bash
chmod +x NumeriPlot.command
```

For a macOS security warning, see the [documented Gatekeeper steps](../README.md).
Do not bypass a damaged-app or malware warning. If you prefer Terminal,
run this from the project folder:

```bash
./venv/bin/python main.py
```

Do not move the project folder after setup: virtual environments are not
portable. If you need to move it, repeat setup in a new source copy.

## 5. Check your first session

Use **File → Open Project…** to open
`examples/NumeriPlot_example_project.json`. Inspect Plot and Analysis Report.
Use **Save Project As…** to save your own copy outside the source folder.
This example uses synthetic data only. Follow the
[illustrated guide](https://alptekin-yildiz.github.io/NumeriPlot/en.html) for
import, fitting, and exports.

After dragging a fit range, reselect the data series in Layer Management,
choose a model, and select **Fit**. Existing fits do not recalculate automatically.

## 6. Troubleshooting

- **Missing `main.py` or `setup.sh`:** Terminal is in the wrong folder. Repeat
  the `cd` method in step 2.
- **`ModuleNotFoundError`:** use `./venv/bin/python main.py`. If installation
  failed, activate the environment and finish `bash setup.sh`.
- **No matching package version / compiler requested:** check Python version
  and architecture. Do not substitute arbitrary dependency versions in
  `requirements.txt`; consult [support](../SUPPORT.md) with the exact error.

### Apple Silicon / Python 3.11: SciPy `_spropack` or `__thread_bss` failure

In the local check, SciPy 1.15.2's macOS 14 wheel failed to load. The same
version's macOS 12 arm64 wheel passed startup and tests. **Only use this
workaround if you encounter that failure on Apple Silicon and Python 3.11.**
Do not force this file onto other architectures or Python versions.

The first two commands confirm the Python series and architecture: expect
`3.11.x` and `arm64`. The following commands download the alternative official
PyPI wheel and replace only SciPy in the project environment, at the same version:

```bash
./venv/bin/python --version
./venv/bin/python -c "import platform; print(platform.machine())"
./venv/bin/python -m pip download --only-binary=:all: --no-deps --platform macosx_12_0_arm64 --python-version 3.11 --implementation cp --abi cp311 --dest venv/wheel-downloads scipy==1.15.2
./venv/bin/python -m pip install --force-reinstall --no-deps venv/wheel-downloads/scipy-1.15.2-cp311-cp311-macosx_12_0_arm64.whl
./venv/bin/python main.py
```

The macOS 12 wheel filename does not establish macOS 12 support for the whole
application. Recreating the environment can reintroduce this issue. This
workaround does not add third-party binaries to the source archive.

For other failures follow [SUPPORT.md](../SUPPORT.md). Remove personal paths
and sensitive data before sharing logs or error messages.

## 7. Update or remove

Save your projects before updating. Download new source into a **separate
folder** and create a fresh environment. Keep the old folder until you have
tested the new version. Do not copy `venv` into the new checkout. Project
schema remains **1.0** in this version.

To remove NumeriPlot, close it, move any data/projects you want to keep to a
different location, and move the source folder to Trash using Finder. This
does not uninstall Python or Homebrew. See [support](../SUPPORT.md) for the
separate local log location.

## 8. Optional: build your own Mac `.app`

This is not necessary for normal use. In a **separate clean source copy**,
first launch the application as described above. Then install development
tools and run the checks. Do not package if the checks fail:

```bash
source venv/bin/activate
bash setup.sh --dev
```

Reapply the SciPy workaround after development setup if necessary. Then run the checks:

```bash
bash release_check.sh
```
 The build
command **deletes and recreates** existing `build/` and `dist/` folders in the
project directory; do not keep files you need in those output folders:

```bash
bash build_macos.sh
```

Output is `dist/NumeriPlot.app` and a versioned ZIP. The packaging spec sets
macOS 14 as the minimum; do not assume builds on other architectures produce
a universal application. No Apple Developer ID signature or notarization is
added. Do not bypass a damaged-app or malware warning. **Redistributing** your
package is a separate action and requires reviewing the
[third-party distribution conditions](../THIRD_PARTY_NOTICES.md); this section
is not distribution clearance.

## References

- [Python virtual environments](https://docs.python.org/3.11/library/venv.html)
- [Python on macOS](https://docs.python.org/3.11/using/mac.html)
- [Homebrew Python 3.11](https://formulae.brew.sh/formula/python@3.11)
- [Downloading GitHub source archives](https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives)
