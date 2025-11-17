from pathlib import Path

from robot.libdocpkg.model import LibraryDoc

from robotframework_find_unused.common.const import KeywordData, LibraryData
from robotframework_find_unused.common.convert import libdoc_keyword_to_keyword_data
from robotframework_find_unused.common.visit import visit_files
from robotframework_find_unused.visitors.keyword_visitor import KeywordVisitor


def get_custom_keyword_definitions(files: list[LibraryDoc]):
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

        for keyword in file.keywords:
            keywords.append(libdoc_keyword_to_keyword_data(keyword, file_type))

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
