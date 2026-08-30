import json

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
