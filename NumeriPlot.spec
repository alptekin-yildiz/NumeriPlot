# -*- mode: python ; coding: utf-8 -*-
# NumeriPlot — PyInstaller spec

import sys
from pathlib import Path

block_cipher = None
project_root = Path(SPECPATH)
sys.path.insert(0, str(project_root))

from src.version import (
    APP_NAME,
    APP_SLUG,
    BUNDLE_ID,
    BUNDLE_SHORT_VERSION,
    BUNDLE_VERSION,
    MACOS_MINIMUM_VERSION,
    VERSION,
)
from tools.bundle_policy import is_excluded_entry

# build_macos.sh collects these notices before PyInstaller runs.
third_party_licenses = project_root / 'build' / 'third-party-licenses'
if not (third_party_licenses / 'THIRD_PARTY_LICENSES.txt').is_file():
    raise SystemExit('Third-party license notices are missing. Build with: bash build_macos.sh')

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        ('LICENSE', '.'),
        ('THIRD_PARTY_NOTICES.md', '.'),
        ('licenses', 'licenses'),
        (str(third_party_licenses), 'licenses/third-party'),
        ('examples/NumeriPlot_example_project.json', 'examples'),
        # Include source needed for model inspection without local bytecode caches.
        *[
            (str(path), str(path.parent.relative_to(project_root)))
            for folder in ('lang', 'models', 'src')
            for path in sorted((project_root / folder).rglob('*.py'))
        ],
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.sip',
        'matplotlib.backends.backend_qtagg',
        'matplotlib.backends.backend_agg',
        'scipy.optimize',
        'scipy.signal',
        'scipy.integrate',
        'pandas',
        'numpy',
        'openpyxl',
        'models.lineer',
        'models.gaussian',
        'models.ustel',
        'models.ustel_saturasyon',
        'models.power_law',
        'src.ui.dialogs',
        'src.ui.dialogs.data_import',
        'src.ui.dialogs.fit',
        'src.ui.dialogs.plot_settings',
        'src.ui.main_window',
        'src.ui.main_window.core',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'jupyter', 'notebook', 'IPython',
        'torch', 'tensorflow', 'sklearn',
        'cv2',
        'tkinter', '_tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Qt parts that only unused plugins pull in (see tools/bundle_policy.py).
a.binaries = [entry for entry in a.binaries if not is_excluded_entry(*entry)]
a.datas = [entry for entry in a.datas if not is_excluded_entry(*entry)]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_SLUG,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name=APP_SLUG,
)

app = BUNDLE(
    coll,
    name=f'{APP_SLUG}.app',
    icon=f'{APP_SLUG}.icns',
    bundle_identifier=BUNDLE_ID,
    version=VERSION,
    info_plist={
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleShortVersionString': BUNDLE_SHORT_VERSION,
        'CFBundleVersion': BUNDLE_VERSION,
        'CFBundleIdentifier': BUNDLE_ID,
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': MACOS_MINIMUM_VERSION,
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
    },
)
