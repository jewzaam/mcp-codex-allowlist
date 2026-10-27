# mcp-codex-allowlist

Read-only MCP server that exposes Codex command execution rules so an agent can
inspect the user's pre-approved command rules before acting.

## Overview

The server reads direct `*.rules` files from the user Codex home and a project’s
`.codex/rules/` directory. It preserves each source file, its path, and scope.
The combined tool returns global and project files in that order without
deduplicating or interpreting rules.

The Python package source is in [mcp_codex_allowlist/](mcp_codex_allowlist/).

This is a view of the rule files, not effective policy. Codex also applies
approval and sandbox settings, managed policy, and project trust. Project rules
are only active when Codex trusts the project.

## Installation

Requires Python 3.10+ and [pipx](https://pipx.pypa.io/).

```bash
git clone https://github.com/jewzaam/mcp-codex-allowlist.git
cd mcp-codex-allowlist
make install-pipx
codex mcp add allowlist -- mcp-codex-allowlist
```

For a non-default Codex home, pass it to the server process:

```bash
codex mcp add allowlist --env CODEX_HOME=/path/to/codex-home -- mcp-codex-allowlist
```

The default is `~/.codex`.

## Usage

| Tool | Returns |
|------|---------|
| `get_global_exec_rules` | User-level rules from `$CODEX_HOME/rules/*.rules`. |
| `get_local_exec_rules` | Project rules from `<project>/.codex/rules/*.rules`. |
| `get_codex_exec_rules` | Both scopes, with per-file scope and source path. |

The two project tools accept an optional `project_dir`; if omitted, the server
uses its current working directory. Each result's `count` fields count rule
files, not individual rules. The files can contain `allow`, `prompt`, or
`forbidden` decisions.

## Development

```bash
make install-dev
make check
```
