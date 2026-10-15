"""NumeriPlot project-file schema I/O."""

from __future__ import annotations

import copy
import json
import os
import stat
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CURRENT_SCHEMA_VERSION = "1.0"
_LEGACY_VERSION = "2.0"


class ProjectSchemaError(ValueError):
    """Raised when a project does not use a supported schema."""


@dataclass(frozen=True)
class LoadedProject:
    """A validated project document and its safe-save requirement."""

    data: dict[str, Any]
    requires_save_as: bool


def read_project(path: str | Path) -> LoadedProject:
    """Read and normalize a supported project document."""
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    if document.get("schema_version") == CURRENT_SCHEMA_VERSION:
        return LoadedProject(data=document, requires_save_as=False)
    if "schema_version" not in document and document.get("version") == _LEGACY_VERSION:
        document.pop("version")
        document["schema_version"] = CURRENT_SCHEMA_VERSION
        return LoadedProject(data=document, requires_save_as=True)
    found_version = document.get("schema_version", document.get("version", "missing"))
    raise ProjectSchemaError(f"Unsupported project schema: {found_version}")


def write_project(path: str | Path, project_data: Mapping[str, Any]) -> None:
    """Write a project using the current public schema version."""
    document = copy.deepcopy(dict(project_data))
    document.pop("version", None)
    document["schema_version"] = CURRENT_SCHEMA_VERSION
    serialized = json.dumps(document, indent=4, ensure_ascii=False)
    # Follow existing symlinks as direct writes did, while replacing the target
    # only after the complete new document has reached disk.
    target = Path(path).resolve()
    try:
        existing_mode = stat.S_IMODE(target.stat().st_mode)
    except FileNotFoundError:
        existing_mode = None
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=".numeriplot-", suffix=".tmp", dir=target.parent
    )
    temporary = Path(temporary_name)
    try:
        try:
            stream = os.fdopen(descriptor, "w", encoding="utf-8")
        except BaseException:
            os.close(descriptor)
            raise
        with stream as output:
            output.write(serialized)
            output.flush()
            os.fsync(output.fileno())
        if existing_mode is not None:
            temporary.chmod(existing_mode)
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
