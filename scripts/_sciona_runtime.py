"""Runtime import helpers for operational scripts."""

from __future__ import annotations

from pathlib import Path
import sys


def ensure_sciona_runtime(repo_root: Path) -> None:
    """Make the matcher-provided `sciona` package importable in local checkouts."""
    try:
        import sciona.physics_ingest  # noqa: F401

        return
    except ModuleNotFoundError:
        pass

    sibling_matcher = repo_root.parent / "sciona-matcher"
    if sibling_matcher.exists() and str(sibling_matcher) not in sys.path:
        sys.path.insert(0, str(sibling_matcher))
