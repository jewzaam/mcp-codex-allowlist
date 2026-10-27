"""Read Codex command execution rules from user and project config layers."""

import os
from pathlib import Path
from typing import Any


def get_codex_home() -> Path:
    """Return Codex's user configuration directory."""
    codex_home = os.environ.get("CODEX_HOME")
    return Path(codex_home).expanduser() if codex_home else Path.home() / ".codex"


def _read_rule_files(directory: Path, *, scope: str) -> list[dict[str, str]]:
    """Read direct .rules files from one Codex config layer."""
    if not directory.is_dir():
        return []
    return [
        {"scope": scope, "path": str(path), "content": path.read_text(encoding="utf-8")}
        for path in sorted(directory.glob("*.rules"))
        if path.is_file()
    ]


def get_global_exec_rules() -> dict[str, Any]:
    """Return Codex's user-level command execution rule files."""
    codex_home = get_codex_home()
    rule_files = _read_rule_files(codex_home / "rules", scope="user")
    return {
        "codex_home": str(codex_home),
        "count": len(rule_files),
        "rule_files": rule_files,
    }


def get_local_exec_rules(*, project_dir: str | None = None) -> dict[str, Any]:
    """Return the project-level command execution rule files."""
    project = Path(project_dir) if project_dir else Path.cwd()
    rule_files = _read_rule_files(project / ".codex" / "rules", scope="project")
    return {
        "project_dir": str(project),
        "count": len(rule_files),
        "rule_files": rule_files,
    }


def get_exec_rules(*, project_dir: str | None = None) -> dict[str, Any]:
    """Return user and project rules in source order without interpreting them."""
    global_data = get_global_exec_rules()
    local_data = get_local_exec_rules(project_dir=project_dir)
    rule_files = global_data["rule_files"] + local_data["rule_files"]
    return {
        "codex_home": global_data["codex_home"],
        "project_dir": local_data["project_dir"],
        "global_count": global_data["count"],
        "local_count": local_data["count"],
        "total_count": len(rule_files),
        "rule_files": rule_files,
    }
