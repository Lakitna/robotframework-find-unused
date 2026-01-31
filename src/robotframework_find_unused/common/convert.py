import functools
import os
import re
from pathlib import Path
from typing import Any, Literal, cast

from robot.libdocpkg.model import KeywordDoc

from robotframework_find_unused.parse.parse_variable import get_variables_in_string

from .const import KeywordData
from .normalize import normalize_keyword_name


def libdoc_keyword_to_keyword_data(
    libdoc: KeywordDoc,
    keyword_type: Literal["CUSTOM_SUITE", "CUSTOM_LIBRARY", "CUSTOM_RESOURCE", "LIBRARY"],
    keyword_returns: bool | None = None,
):
    """
    Convert a Libdoc keyword to the internally used data structure
    """
    argument_use_count = {}
    for arg in libdoc.args.argument_names:
        argument_use_count[arg] = 0

    normalized_name = normalize_keyword_name(libdoc.name)
    name_parts = get_keyword_name_parts(normalized_name)

    return KeywordData(
        name=libdoc.name,
        normalized_name=normalized_name,
        name_parts=name_parts,
        name_match_pattern=get_keyword_name_match_pattern(name_parts),
        library=cast(Any, libdoc.parent).name,
        deprecated=(libdoc.deprecated is True),
        private=("robot:private" in libdoc.tags),
        argument_use_count=argument_use_count,
        arguments=libdoc.args,
        use_count=0,
        returns=keyword_returns,
        return_use_count=0,
        type=keyword_type,
    )


def get_keyword_name_parts(name: str) -> list[str]:
    """Cut keyword name into parts based on embedded variables."""
    name_vars = get_variables_in_string(name)
    if len(name_vars) == 0:
        return [name]

    name_parts = []
    for var in name_vars:
        (part, name) = name.split(var, maxsplit=1)
        name_parts.append(part)
        name_parts.append("__VARIABLE__")

    if name:
        name_parts.append(name)

    return name_parts


def get_keyword_name_match_pattern(name_parts: list[str]) -> re.Pattern:
    """Build regex pattern that allows for matching calls to keywords with embedded args"""
    pattern = "^"
    for part in name_parts:
        if part == "__VARIABLE__":
            pattern += ".+?"
        else:
            pattern += re.escape(part)
    pattern += "$"
    return re.compile(pattern)


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
