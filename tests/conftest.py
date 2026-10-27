"""Global safety guards for tests."""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def _block_real_filesystem(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Block pathlib mutations outside tmp_path and the project virtualenv."""

    def is_allowed(path: Path) -> bool:
        resolved = path.resolve()
        return any(
            resolved == root or root in resolved.parents
            for root in (tmp_path.resolve(), PROJECT_ROOT / ".venv")
        )

    def guard(original):
        def guarded(self, *args, **kwargs):
            if not is_allowed(self):
                raise PermissionError(f"Test tried to write outside tmp_path: {self}")
            return original(self, *args, **kwargs)

        return guarded

    for method in ("write_text", "write_bytes", "rename", "unlink", "rmdir", "mkdir"):
        monkeypatch.setattr(Path, method, guard(getattr(Path, method)))
