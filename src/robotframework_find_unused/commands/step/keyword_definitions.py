from typing import cast

from robot.libdocpkg.model import KeywordDoc, LibraryDoc

from robotframework_find_unused.common.const import KeywordData
from robotframework_find_unused.convert.convert_keyword import libdoc_keyword_to_keyword_data
from robotframework_find_unused.reporter.base.partial.keyword_definitions import (
    PartialReporter_CustomKeywordDefinitions,
)
from robotframework_find_unused.resolve.resolve_python_keyword_data import (
    enrich_python_keyword_data,
)


def step_step_get_custom_keyword_definitions(
    files: list[LibraryDoc],
    *,
    reporter: PartialReporter_CustomKeywordDefinitions,
    enrich_py_keywords: bool = False,
):
    """
    Gather keyword definitions in the given scope with LibDoc and show progress
    """
    reporter.on_get_custom_keyword_definitions_start(files)

    keywords = _get_custom_keyword_definitions(
        files,
        enrich_py_keywords=enrich_py_keywords,
    )

    reporter.on_get_custom_keyword_definitions_end(files, keywords)
    return keywords


def _get_custom_keyword_definitions(
    files: list[LibraryDoc],
    *,
    enrich_py_keywords: bool = False,
) -> list[KeywordData]:
    """
    Gather keyword definitions in the given scope with LibDoc

    Libdoc supports .robot, .resource, .py, and downloaded libs
    """
    keywords: list[KeywordData] = []
    for file in files:
        if file.type == "SUITE":
            file_type = "CUSTOM_SUITE"
        elif file.type == "LIBRARY":
            file_type = "CUSTOM_LIBRARY"
        elif file.type == "RESOURCE":
            file_type = "CUSTOM_RESOURCE"
        else:
            raise ValueError("Unexpected file type " + file.type)

        if file_type == "CUSTOM_LIBRARY" and enrich_py_keywords:
            enriched_keywords = enrich_python_keyword_data(file)
            for keyword in enriched_keywords:
                keywords.append(
                    libdoc_keyword_to_keyword_data(
                        keyword.doc,
                        file_type,
                        keyword.returns,
                    ),
                )
        else:
            # LibDoc provides all the data we need
            for keyword in cast(list[KeywordDoc], file.keywords):
                keywords.append(
                    libdoc_keyword_to_keyword_data(
                        keyword,
                        file_type,
                        # We don't care or will gather this later
                        keyword_returns=None,
                    ),
                )

    return keywords
