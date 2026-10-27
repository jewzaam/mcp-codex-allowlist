"""Tests for MCP tool registration and results."""

from unittest.mock import patch

import pytest

from mcp_codex_allowlist.mcp_server import get_codex_exec_rules, server
from mcp_codex_allowlist.mcp_server import get_global_exec_rules, get_local_exec_rules
from mcp_codex_allowlist.mcp_server import main


@pytest.mark.asyncio
async def test_server_exposes_global_local_and_merged_tools():
    tools = await server.list_tools()

    assert {tool.name for tool in tools} == {
        "get_global_exec_rules",
        "get_local_exec_rules",
        "get_codex_exec_rules",
    }


@pytest.mark.asyncio
async def test_global_tool_wraps_user_rules_with_source():
    with patch(
        "mcp_codex_allowlist.mcp_server.read_global_exec_rules",
        return_value={"codex_home": "/tmp/codex", "count": 1, "rule_files": []},
    ):
        result = await server.call_tool("get_global_exec_rules", {})

    assert result.structured_content == {
        "source": "global",
        "codex_home": "/tmp/codex",
        "count": 1,
        "rule_files": [],
    }


@pytest.mark.asyncio
async def test_local_tool_passes_project_dir():
    with patch(
        "mcp_codex_allowlist.mcp_server.read_local_exec_rules",
        return_value={"project_dir": "/tmp/project", "count": 0, "rule_files": []},
    ) as read_rules:
        result = await server.call_tool(
            "get_local_exec_rules", {"project_dir": "/tmp/project"}
        )

    read_rules.assert_called_once_with(project_dir="/tmp/project")
    assert result.structured_content["source"] == "local"


@pytest.mark.asyncio
async def test_combined_tool_returns_user_and_project_rules():
    merged = {
        "codex_home": "/tmp/codex",
        "project_dir": "/tmp/project",
        "global_count": 1,
        "local_count": 2,
        "total_count": 3,
        "rule_files": [],
    }
    with patch("mcp_codex_allowlist.mcp_server.get_exec_rules", return_value=merged):
        result = await server.call_tool(
            "get_codex_exec_rules", {"project_dir": "/tmp/project"}
        )

    assert result.structured_content == {"source": "merged", **merged}


def test_tool_functions_are_callable_directly():
    assert get_global_exec_rules()["source"] == "global"
    assert get_local_exec_rules(project_dir="/missing")["source"] == "local"
    assert get_codex_exec_rules(project_dir="/missing")["source"] == "merged"


def test_main_starts_stdio_server():
    with patch.object(server, "run") as run:
        main()

    run.assert_called_once_with(transport="stdio")
