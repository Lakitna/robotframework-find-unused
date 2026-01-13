from pathlib import Path


def normalize_variable_name(name: str, *, strip_decoration: bool = True) -> str:
    """
    Normalize Robot variables name. Output is suitable for matching and sorting purposes
    """
    norm = name.replace(" ", "").replace("_", "").lower()

    if strip_decoration and norm[0] in ("$", "@", "&", "%"):
        norm = norm[1:].removeprefix("{").removesuffix("}")

    return norm


def normalize_keyword_name(name: str) -> str:
    """
    Normalize Robot keyword name. Output is suitable for matching and sorting purposes
    """
    return name.replace(" ", "").replace("_", "").lower()


def normalize_library_name(name: str) -> str:
    """
    Normalize Robot library name. Output is suitable for matching and sorting purposes
    """
    return normalize_keyword_name(name)


def normalize_file_path(path: str | Path) -> str:
    """
    Normalize file path. Output is suitable for matching and sorting purposes
    """
    if isinstance(path, str):
        path = Path(path)

    return path.resolve().as_posix()
