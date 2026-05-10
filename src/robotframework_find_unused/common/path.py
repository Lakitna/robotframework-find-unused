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
    """
    if path_in_venv(path):
        return False

    try:
        path.relative_to(root_directory)
    except ValueError:
        # Is not child of root
        return False

    return True


@cache
def path_in_venv(path: Path) -> bool:
    """
    Return true if the path is inside a virtual environment.
    """
    parts = [p.casefold() for p in path.parts]
    return bool("lib" in parts and "site-packages" in parts)
