from pathlib import Path
from typing import cast

from robot.libdocpkg.model import KeywordDoc, LibraryDoc

from robotframework_find_unused.visitors.keyword_visitor import KeywordVisitor

from .const import KeywordData, LibraryData
from .convert import libdoc_keyword_to_keyword_data
from .enrich_python_keywords import enrich_python_keyword_data
from .visit import visit_files


def get_custom_keyword_definitions(
    files: list[LibraryDoc],
    *,
    enrich_py_keywords: bool = False,
):
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


def count_keyword_uses(
    file_paths: list[Path],
    keywords: list[KeywordData],
    downloaded_library_keywords: list[LibraryData],
):
    """
    Walk through all robot files to count keyword uses.
    """
    visitor = KeywordVisitor(keywords, downloaded_library_keywords)
    visit_files(file_paths, visitor)
    return list(visitor.keywords.values())
