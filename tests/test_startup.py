"""Startup checks must repair only the known wheel failure and fail clearly."""
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from src import runtime_check as check

ROOT = Path(__file__).resolve().parents[1]
ERROR = '_spropack: __thread_bss invalid offset'


@pytest.mark.parametrize('override', [
    {}, {'system': 'Linux'}, {'machine': 'x86_64'}, {'mac_version': '26.0'},
    {'python_version': (3, 12)}, {'scipy_version': '1.16.0'}, {'error': 'another failure'},
])
def test_repair_is_narrowly_scoped(override):
    inputs = dict(error=ERROR, system='Darwin', machine='arm64', mac_version='27.0.1',
                  python_version=(3, 11), scipy_version='1.15.2')
    inputs.update(override)
    assert check.eligible_for_repair(**inputs) == (not override)


@pytest.mark.parametrize('repair_enabled,after,expected', [(True, 0, 0), (True, 1, 1), (False, 0, 1)])
def test_repair_rechecks_and_preserves_failure(tmp_path, monkeypatch, repair_enabled, after, expected):
    monkeypatch.setattr(check, 'ROOT', tmp_path)
    results = iter([SimpleNamespace(returncode=1, stdout='', stderr=ERROR),
                    SimpleNamespace(returncode=after, stdout='', stderr='still broken' if after else '')])
    monkeypatch.setattr(check, 'probe', lambda: next(results))
    monkeypatch.setattr(check, 'eligible_for_repair', lambda *args: True)
    calls = []
    monkeypatch.setattr(check, 'repair', lambda: calls.append('repair'))
    assert check.main(['--repair'] if repair_enabled else []) == expected
    assert calls == (['repair'] if repair_enabled else [])
    assert ERROR in (tmp_path / 'venv/runtime-check.log').read_text()


def test_exception_before_qapplication_does_not_abort():
    script = '''
import main
from pathlib import Path
main._make_exception_handler(Path('/tmp/synthetic.log'))(ImportError, ImportError('synthetic'), None)
print('handled')
'''
    result = subprocess.run([sys.executable, '-c', script], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0
    assert 'handled' in result.stdout
    assert 'Guide section 6' in result.stderr


def test_logging_is_quiet_and_bounded(tmp_path):
    script = '''
import main, logging
from pathlib import Path
main.Path.home = lambda: Path(__import__('sys').argv[1])
path = main._setup_logging()
logging.debug('debug noise')
logging.getLogger('matplotlib.font_manager').warning('font noise')
logging.warning('visible warning')
logging.warning('')
handler = logging.getLogger().handlers[0]
handler.maxBytes = 200
for i in range(30):
    logging.info('bounded log record %s xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', i)
logging.shutdown()
assert len(list(path.parent.glob('numeriplot.log*'))) <= 4
assert path.stat().st_size <= 200
'''
    result = subprocess.run([sys.executable, '-c', script, str(tmp_path)], cwd=ROOT,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stderr.strip() == 'WARNING: visible warning\nWARNING:'


def test_setup_handles_spaces_unicode_and_different_working_directory(tmp_path):
    import shutil
    import shlex
    import os
    folder = tmp_path / 'Tez Çalışması 2'
    folder.mkdir()
    shutil.copy2(ROOT / 'setup.sh', folder)
    shutil.copytree(ROOT / 'src', folder / 'src', ignore=shutil.ignore_patterns('__pycache__'))
    bin_dir = folder / 'venv/bin'
    bin_dir.mkdir(parents=True)
    interpreter = bin_dir / 'python3'
    interpreter.write_text(
        '#!/bin/bash\n'
        'if [ "$1" = -m ]; then exit 0; fi\n'
        f'exec {shlex.quote(sys.executable)} "$@"\n'
    )
    interpreter.chmod(0o755)
    (bin_dir / 'activate').write_text(f'export PATH={shlex.quote(str(bin_dir))}:"$PATH"\n')
    env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ['PATH'])
    result = subprocess.run(['bash', str(folder / 'setup.sh')], cwd=tmp_path,
                            env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert 'Setup complete' in result.stdout


def test_healthy_imports_never_repair(tmp_path, monkeypatch):
    monkeypatch.setattr(check, 'ROOT', tmp_path)
    monkeypatch.setattr(check, 'probe', lambda: SimpleNamespace(returncode=0, stdout='', stderr=''))
    monkeypatch.setattr(check, 'repair', lambda: pytest.fail('healthy installation must not be changed'))
    assert check.main(['--repair']) == 0


def test_unrelated_import_error_never_repairs(tmp_path, monkeypatch):
    monkeypatch.setattr(check, 'ROOT', tmp_path)
    monkeypatch.setattr(check, 'probe', lambda: SimpleNamespace(returncode=1, stdout='', stderr='missing PyQt6'))
    monkeypatch.setattr(check, 'repair', lambda: pytest.fail('unrelated error must not change SciPy'))
    assert check.main(['--repair']) == 1


def test_repair_download_failure_stops_setup(tmp_path, monkeypatch):
    monkeypatch.setattr(check, 'ROOT', tmp_path)
    monkeypatch.setattr(check, 'probe', lambda: SimpleNamespace(returncode=1, stdout='', stderr=ERROR))
    monkeypatch.setattr(check, 'eligible_for_repair', lambda *args: True)
    def fail_download():
        raise subprocess.CalledProcessError(1, ['pip', 'download'])
    monkeypatch.setattr(check, 'repair', fail_download)
    assert check.main(['--repair']) == 1


@pytest.mark.parametrize('existing_venv', [True, False])
def test_setup_chooses_311_without_activation(tmp_path, existing_venv):
    import os
    import shlex
    import shutil
    folder = tmp_path / 'Tez Çalışması 2'
    folder.mkdir()
    shutil.copy2(ROOT / 'setup.sh', folder)
    shutil.copytree(ROOT / 'src', folder / 'src', ignore=shutil.ignore_patterns('__pycache__'))
    commands = tmp_path / 'commands'
    commands.mkdir()
    old_python = commands / 'python3'
    old_python.write_text('#!/bin/bash\necho "wrong system Python 3.9 selected" >&2\nexit 39\n')
    old_python.chmod(0o755)
    wrapper = (
        '#!/bin/bash\n'
        'if [ "$1" = -m ]; then\n'
        '  if [ "$2" = venv ]; then\n'
        '    mkdir -p venv/bin\n'
        '    cp "$0" venv/bin/python3\n'
        '    echo \'export PATH="$PWD/venv/bin:$PATH"\' > venv/bin/activate\n'
        '  fi\n'
        '  exit 0\n'
        'fi\n'
        f'exec {shlex.quote(sys.executable)} "$@"\n'
    )
    if existing_venv:
        interpreter = folder / 'venv/bin/python3'
        interpreter.parent.mkdir(parents=True)
        (interpreter.parent / 'activate').write_text('export PATH="$PWD/venv/bin:$PATH"\n')
    else:
        interpreter = commands / 'python3.11'
    interpreter.write_text(wrapper)
    interpreter.chmod(0o755)
    env = dict(os.environ, PATH=str(commands) + ':/usr/bin:/bin')
    result = subprocess.run(['/bin/bash', str(folder / 'setup.sh')], cwd=tmp_path,
                            env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert 'Setup complete' in result.stdout


@pytest.mark.parametrize('launcher', [False, True])
def test_startup_recovery_is_not_duplicated_and_traceback_stays_in_log(tmp_path, launcher):
    import os
    script = '''
import main
from pathlib import Path
main.Path.home = lambda: Path(__import__('sys').argv[1])
path = main._setup_logging()
main._make_exception_handler(path)(ImportError, ImportError('synthetic failure'), None)
assert 'synthetic failure' in path.read_text()
'''
    result = subprocess.run([sys.executable, '-c', script, str(tmp_path)], cwd=ROOT,
                            env=dict(os.environ, NUMERIPLOT_LAUNCHER='1' if launcher else ''),
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert 'could not start' in result.stderr
    assert 'CRITICAL' not in result.stderr
    assert ('Guide section 6' in result.stderr) is not launcher


def test_setup_preserves_broken_environment(tmp_path):
    import shutil
    shutil.copy2(ROOT / 'setup.sh', tmp_path)
    env_dir = tmp_path / 'venv'
    env_dir.mkdir()
    marker = env_dir / 'keep.txt'
    marker.write_text('existing environment')
    result = subprocess.run(['/bin/bash', str(tmp_path / 'setup.sh')],
                            capture_output=True, text=True)
    assert result.returncode == 1
    assert 'fresh source copy' in result.stdout
    assert marker.read_text() == 'existing environment'
