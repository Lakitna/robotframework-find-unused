import functools
import os
from pathlib import Path


@functools.cache
def to_relative_path(parent: Path, child: Path) -> str:
    """
    Get relative file path from parent to child. Output suitable for user output.
    """
    rel_path = os.path.relpath(child.resolve(), parent.resolve())
    rel_path = Path(rel_path).as_posix()

    if not rel_path.startswith("."):
        rel_path = f"./{rel_path}"

    return rel_path
