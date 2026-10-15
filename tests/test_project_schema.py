import json
import os
import stat
from contextlib import contextmanager

import pytest

from src.project_schema import ProjectSchemaError, read_project, write_project


def test_new_project_is_written_with_schema_version_1(tmp_path):
    path = tmp_path / "project.json"

    write_project(path, {"raw_data": "x,y\n0,1\n", "version": "2.0"})

    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["schema_version"] == "1.0"
    assert "version" not in saved
    assert saved["raw_data"] == "x,y\n0,1\n"


def test_current_project_schema_is_read_without_save_as(tmp_path):
    path = tmp_path / "project.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "raw_data": "x,y\n0,1\n",
                "series": [],
            }
        ),
        encoding="utf-8",
    )

    loaded = read_project(path)

    assert loaded.requires_save_as is False
    assert loaded.data["schema_version"] == "1.0"
    assert loaded.data["raw_data"] == "x,y\n0,1\n"


def test_legacy_v2_project_is_normalized_in_memory_and_requires_save_as(tmp_path):
    path = tmp_path / "legacy.json"
    original = json.dumps(
        {
            "version": "2.0",
            "raw_data": "x,y\n0,1\n",
            "series": [{"label": "Synthetic series"}],
        },
        indent=2,
    )
    path.write_text(original, encoding="utf-8")

    loaded = read_project(path)

    assert loaded.requires_save_as is True
    assert loaded.data["schema_version"] == "1.0"
    assert "version" not in loaded.data
    assert loaded.data["series"] == [{"label": "Synthetic series"}]
    assert path.read_text(encoding="utf-8") == original


def test_unknown_new_schema_is_rejected(tmp_path):
    path = tmp_path / "future.json"
    path.write_text(
        json.dumps({"schema_version": "2.0", "raw_data": "x,y\n0,1\n"}),
        encoding="utf-8",
    )

    with pytest.raises(ProjectSchemaError, match="2.0"):
        read_project(path)


def test_serialization_failure_preserves_existing_project(tmp_path):
    path = tmp_path / "project.json"
    original = b'{"schema_version": "1.0", "series": []}'
    path.write_bytes(original)

    with pytest.raises(TypeError):
        write_project(path, {"unsupported": object()})

    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


def test_partial_write_failure_preserves_existing_project(monkeypatch, tmp_path):
    path = tmp_path / "project.json"
    original = b'{"schema_version": "1.0", "series": []}'
    path.write_bytes(original)
    real_fdopen = os.fdopen

    @contextmanager
    def failing_fdopen(*args, **kwargs):
        with real_fdopen(*args, **kwargs) as stream:
            class FailingWriter:
                def write(self, text):
                    stream.write(text[:10])
                    stream.flush()
                    raise OSError("synthetic write failure")
            yield FailingWriter()

    monkeypatch.setattr(os, "fdopen", failing_fdopen)

    with pytest.raises(OSError, match="synthetic write failure"):
        write_project(path, {"series": []})

    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


def test_replace_failure_preserves_existing_project(monkeypatch, tmp_path):
    path = tmp_path / "project.json"
    original = b'{"schema_version": "1.0", "series": []}'
    path.write_bytes(original)

    def failing_replace(source, destination):
        assert source.parent == path.parent
        assert json.loads(source.read_text())["schema_version"] == "1.0"
        raise OSError("synthetic replace failure")

    monkeypatch.setattr(os, "replace", failing_replace)

    with pytest.raises(OSError, match="synthetic replace failure"):
        write_project(path, {"series": []})

    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


def test_successful_save_preserves_existing_permissions(tmp_path):
    path = tmp_path / "project.json"
    path.write_text("{}", encoding="utf-8")
    path.chmod(0o640)

    write_project(path, {"series": []})

    assert stat.S_IMODE(path.stat().st_mode) == 0o640
    assert json.loads(path.read_text())["schema_version"] == "1.0"
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize("existing", [False, True])
def test_sync_failure_leaves_destination_unchanged(monkeypatch, tmp_path, existing):
    path = tmp_path / "project.json"
    original = b'{"schema_version": "1.0", "series": []}'
    if existing:
        path.write_bytes(original)

    def failing_sync(_descriptor):
        raise OSError("synthetic sync failure")

    monkeypatch.setattr(os, "fsync", failing_sync)

    with pytest.raises(OSError, match="synthetic sync failure"):
        write_project(path, {"series": []})

    if existing:
        assert path.read_bytes() == original
        assert list(tmp_path.iterdir()) == [path]
    else:
        assert list(tmp_path.iterdir()) == []


def test_save_through_symlink_updates_target_and_preserves_link(tmp_path):
    target = tmp_path / "target.json"
    target.write_text("{}", encoding="utf-8")
    link = tmp_path / "project.json"
    link.symlink_to(target.name)

    write_project(link, {"series": []})

    assert link.is_symlink()
    assert json.loads(target.read_text())["schema_version"] == "1.0"
    assert set(tmp_path.iterdir()) == {target, link}
