"""Tests for Codex command rule discovery."""

from pathlib import Path

from mcp_codex_allowlist.settings import (
    get_codex_home,
    get_exec_rules,
    get_global_exec_rules,
    get_local_exec_rules,
)


def _write_rule(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def test_get_codex_home_defaults_to_dot_codex(monkeypatch, tmp_path):
    monkeypatch.delenv("CODEX_HOME", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    assert get_codex_home() == tmp_path / ".codex"


def test_get_global_exec_rules_reads_codex_home(monkeypatch, tmp_path):
    _write_rule(
        tmp_path / "rules" / "default.rules",
        'prefix_rule(pattern=["git"], decision="allow")',
    )
    monkeypatch.setenv("CODEX_HOME", str(tmp_path))

    result = get_global_exec_rules()

    assert result["codex_home"] == str(tmp_path)
    assert result["count"] == 1
    assert result["rule_files"] == [
        {
            "scope": "user",
            "path": str(tmp_path / "rules" / "default.rules"),
            "content": 'prefix_rule(pattern=["git"], decision="allow")',
        }
    ]


def test_get_global_exec_rules_missing_directory_returns_empty(monkeypatch, tmp_path):
    monkeypatch.setenv("CODEX_HOME", str(tmp_path))

    result = get_global_exec_rules()

    assert result["count"] == 0
    assert result["rule_files"] == []


def test_get_local_exec_rules_sorts_files_and_keeps_rule_contents(tmp_path):
    _write_rule(
        tmp_path / ".codex" / "rules" / "z-last.rules", 'prefix_rule(pattern=["z"])'
    )
    _write_rule(
        tmp_path / ".codex" / "rules" / "a-first.rules", 'prefix_rule(pattern=["a"])'
    )

    result = get_local_exec_rules(project_dir=str(tmp_path))

    assert result["project_dir"] == str(tmp_path)
    assert result["count"] == 2
    assert [Path(item["path"]).name for item in result["rule_files"]] == [
        "a-first.rules",
        "z-last.rules",
    ]
    assert all(item["scope"] == "project" for item in result["rule_files"])


def test_get_local_exec_rules_missing_directory_returns_empty(tmp_path):
    result = get_local_exec_rules(project_dir=str(tmp_path))

    assert result["count"] == 0
    assert result["rule_files"] == []


def test_get_exec_rules_preserves_both_scopes_and_duplicate_rules(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "codex-home"))
    content = 'prefix_rule(pattern=["git", "status"], decision="allow")'
    _write_rule(tmp_path / "codex-home" / "rules" / "default.rules", content)
    _write_rule(tmp_path / "project" / ".codex" / "rules" / "default.rules", content)

    result = get_exec_rules(project_dir=str(tmp_path / "project"))

    assert result["global_count"] == 1
    assert result["local_count"] == 1
    assert result["total_count"] == 2
    assert [item["scope"] for item in result["rule_files"]] == ["user", "project"]
    assert [item["content"] for item in result["rule_files"]] == [content, content]
