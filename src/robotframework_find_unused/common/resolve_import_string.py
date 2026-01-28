from pathlib import Path

from .const import VariableValue
from .resolve_variables import resolve_variables


def resolve_import_string(import_str: str, relative_to: Path) -> Path:
    """
    Resolve a file import string.

    Returns absolute Path.
    """
    variables = {
        "curdir": VariableValue(normalized_name="curdir", value="."),
    }
    (import_str, _) = resolve_variables(import_str, variables)

    return relative_to.joinpath(import_str)
