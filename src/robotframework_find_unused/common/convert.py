import functools
import os
from pathlib import Path
from typing import Any, Literal, cast

from robot.libdocpkg.model import KeywordDoc

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

    return KeywordData(
        normalized_name=normalize_keyword_name(libdoc.name),
        name=libdoc.name,
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
