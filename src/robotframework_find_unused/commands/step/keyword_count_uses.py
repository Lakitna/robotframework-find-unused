from typing import TYPE_CHECKING

from robotframework_find_unused.commands.keywords.options import KeywordOptions
from robotframework_find_unused.visitors.robot import visit_robot_files
from robotframework_find_unused.visitors.robot.keyword_visitor import RobotVisitorKeywords

if TYPE_CHECKING:
    from pathlib import Path

    from robotframework_find_unused.common.const import KeywordData, LibraryData
    from robotframework_find_unused.reporter.base.partial.count_keywords import (
        PartialReporter_CountKeywords,
    )


def step_count_keyword_uses(
    file_paths: "list[Path]",
    keywords: "list[KeywordData]",
    downloaded_libraries: "list[LibraryData]",
    *,
    reporter: "PartialReporter_CountKeywords",
):
    """
    Walk through all robot files to count keyword uses and keep the user up-to-date on progress
    """
    reporter.on_count_keyword_uses_start(file_paths, keywords, downloaded_libraries)

    visitor = RobotVisitorKeywords(keywords, downloaded_libraries)
    visit_robot_files(file_paths, visitor)
    counted_keywords = list(visitor.keywords.values())

    if (
        reporter.options.library_keywords != "exclude"
        and reporter.options.unused_library_keywords != "exclude"
    ):
        for lib in downloaded_libraries:
            for kw in lib.keywords:
                if kw in counted_keywords:
                    continue
                counted_keywords.append(kw)

    reporter.on_count_keyword_uses_end(file_paths, keywords, downloaded_libraries, counted_keywords)
    return counted_keywords
