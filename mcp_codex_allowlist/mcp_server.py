"""MCP server exposing Codex command execution rules."""

from typing import Any

from mcp.server.mcpserver import MCPServer

from . import __version__
from .settings import get_exec_rules, get_global_exec_rules as read_global_exec_rules
from .settings import get_local_exec_rules as read_local_exec_rules

server = MCPServer(name="mcp-codex-allowlist", version=__version__)


@server.tool()
def get_global_exec_rules() -> dict[str, Any]:
    """Read user rules from $CODEX_HOME/rules/*.rules (default ~/.codex)."""
    return {"source": "global", **read_global_exec_rules()}


@server.tool()
def get_local_exec_rules(*, project_dir: str | None = None) -> dict[str, Any]:
    """Read rules from the project .codex/rules directory for trusted projects."""
    return {"source": "local", **read_local_exec_rules(project_dir=project_dir)}


@server.tool()
def get_codex_exec_rules(*, project_dir: str | None = None) -> dict[str, Any]:
    """Read user and project rule files with their source scope and paths.

    Files can contain allow, prompt, and forbidden rules. This tool does not compute
    effective policy from approval settings, sandbox settings, managed policy, or
    project trust.
    """
    return {"source": "merged", **get_exec_rules(project_dir=project_dir)}


def main() -> None:
    """Run the MCP server over stdio."""
    server.run(transport="stdio")
