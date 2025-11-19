from typing import Any, Literal, cast

from robocop.linter.utils.misc import normalize_robot_name
from robot.libdocpkg.model import KeywordDoc

from robotframework_find_unused.common.const import KeywordData


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
        normalized_name=normalize_robot_name(libdoc.name),
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
