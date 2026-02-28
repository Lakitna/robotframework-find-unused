from functools import cache
from pathlib import Path


@cache
def path_exists(path: Path) -> bool:
    """
    Return true if the file at path exists. Cached.
    """
    if not path.is_absolute():
        return path_exists(path.resolve())

    return path.exists()


@cache
def path_in_scope(path: Path, root_directory: Path) -> bool:
    """
    Return true if the path is in scope.

    Out of scope if:
    - Not a child of the root_directory
    - In a virtual environment
    """
    try:
        path.relative_to(root_directory)
    except ValueError:
        # Is not child of root
        return False

    parts = [p.casefold() for p in path.parts]
    if "lib" in parts and "site-packages" in parts:  # noqa: SIM103
        # Is a downloaded dependency
        # We can only get here if root_directory contains a virtual environment
        return False

    return True
