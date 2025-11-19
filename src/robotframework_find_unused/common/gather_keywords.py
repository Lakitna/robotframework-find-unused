import ast
from pathlib import Path
from typing import cast

from robot.libdocpkg.model import KeywordDoc, LibraryDoc

from robotframework_find_unused.common.const import KeywordData, LibraryData
from robotframework_find_unused.common.convert import libdoc_keyword_to_keyword_data
from robotframework_find_unused.common.visit import visit_files
from robotframework_find_unused.visitors.keyword_visitor import KeywordVisitor
from robotframework_find_unused.visitors.python_keyword_visitor import (
    EnrichedKeywordDoc,
    PythonKeywordVisitor,
)


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
            for keyword in _enrich_python_keyword_data(file):
                keywords.append(
                    libdoc_keyword_to_keyword_data(
                        keyword.doc,
                        keyword.type,
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


def _enrich_python_keyword_data(libdoc: LibraryDoc) -> list[EnrichedKeywordDoc]:
    """Gather data on Python keyword returns"""
    source_path = Path(cast(str, libdoc.source))
    with source_path.open() as f:
        raw_python_source = f.read()
    model = ast.parse(raw_python_source)

    visitor = PythonKeywordVisitor(libdoc.keywords)
    visitor.visit(model)

    return visitor.keywords
