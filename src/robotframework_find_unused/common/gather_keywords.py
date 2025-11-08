from robocop.config import ConfigManager
from robot.libdocpkg.model import LibraryDoc

from robotframework_find_unused.common.const import KeywordData, LibraryData
from robotframework_find_unused.common.convert import libdoc_keyword_to_keyword_data
from robotframework_find_unused.common.robocop_visit import visit_files_with_robocop
from robotframework_find_unused.visitors.keyword_visitor import KeywordVisitor


def get_keyword_definitions_from_files(files: list[LibraryDoc]):
    """
    Gather keyword definitions in the given scope with LibDoc

    Libdoc supports .robot, .resource, .py, and downloaded libs
    """
    keywords: list[KeywordData] = []
    for file in files:
        file_type = "CUSTOM_" + file.type

        for keyword in file.keywords:
            keywords.append(libdoc_keyword_to_keyword_data(keyword, file_type))

    return keywords


def count_keyword_uses(
    robocop_config: ConfigManager,
    keywords: list[KeywordData],
    downloaded_library_keywords: list[LibraryData],
):
    """
    Walk through all robot files with RoboCop to count keyword uses.
    """
    visitor = KeywordVisitor(keywords, downloaded_library_keywords)
    visit_files_with_robocop(robocop_config, visitor)
    return list(visitor.keywords.values())
