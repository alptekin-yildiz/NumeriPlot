"""Check source-install imports; narrowly repair the known macOS SciPy wheel issue."""
import argparse
import importlib.metadata
import platform
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def probe():
    return subprocess.run(
        [sys.executable, '-c', 'from src.ui.main_window import MainWindow'],
        cwd=ROOT, capture_output=True, text=True, timeout=120,
    )


def eligible_for_repair(error, system, machine, mac_version, python_version, scipy_version):
    return (
        system == 'Darwin' and machine == 'arm64'
        and mac_version.split('.')[0] == '27'
        and tuple(python_version[:2]) == (3, 11)
        and scipy_version == '1.15.2'
        and '_spropack' in error and '__thread_bss' in error
    )


def repair():
    # Download only the documented same-version wheel, never build from source.
    with tempfile.TemporaryDirectory(prefix='numeriplot-wheel-') as folder:
        subprocess.run([
            sys.executable, '-m', 'pip', 'download', '--index-url', 'https://pypi.org/simple',
            '--only-binary=:all:', '--no-deps', '--platform', 'macosx_12_0_arm64',
            '--python-version', '3.11', '--implementation', 'cp', '--abi', 'cp311',
            '--dest', folder, 'scipy==1.15.2',
        ], check=True)
        wheel = Path(folder) / 'scipy-1.15.2-cp311-cp311-macosx_12_0_arm64.whl'
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '--force-reinstall', '--no-deps', str(wheel),
        ], check=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repair', action='store_true')
    args = parser.parse_args(argv)
    report = ROOT / 'venv' / 'runtime-check.log'
    report.parent.mkdir(exist_ok=True)
    try:
        result = probe()
        report.write_text(result.stdout + result.stderr, encoding='utf-8')
        if result.returncode == 0:
            print('Açılış kontrolü başarılı. / Startup import check passed.')
            return 0
        try:
            scipy_version = importlib.metadata.version('scipy')
        except importlib.metadata.PackageNotFoundError:
            scipy_version = ''
        if args.repair and eligible_for_repair(
            result.stderr, platform.system(), platform.machine(), platform.mac_ver()[0],
            sys.version_info, scipy_version,
        ):
            print('Bilinen SciPy açılış hatası: aynı sürümün uyumlu paketi kuruluyor.\n'
                  'Known SciPy startup error: installing the compatible wheel of the same version.', flush=True)
            repair()
            result = probe()
            with report.open('a', encoding='utf-8') as stream:
                stream.write('\nAfter repair:\n' + result.stdout + result.stderr)
            if result.returncode == 0:
                print('Düzeltme ve açılış kontrolü başarılı. / Repair and import check passed.')
                return 0
    except (OSError, subprocess.SubprocessError) as error:
        with report.open('a', encoding='utf-8') as stream:
            stream.write('\n' + str(error))
    print('Kurulum doğrulanamadı. / Setup could not be verified.\n'
          'Kılavuz / Guide: docs/SOURCE_INSTALL_TR.md / docs/SOURCE_INSTALL.md\n'
          'Bölüm 6: Sorun giderme / Section 6: Troubleshooting\n'
          'Ayrıntılar / Details: venv/runtime-check.log\n'
          'Paylaşmadan kişisel yolları temizleyin. / Remove personal paths before sharing.')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
