from pathlib import Path

from robotframework_find_unused.reporter.base.partial.keyword_definitions import (
    PartialReporter_DownloadedKeywordDefinitions,
)
from robotframework_find_unused.visitors.robot import visit_robot_files
from robotframework_find_unused.visitors.robot.library_import import RobotVisitorLibraryImports


def cli_step_get_downloaded_lib_keywords(
    file_paths: list[Path],
    *,
    reporter: PartialReporter_DownloadedKeywordDefinitions,
    enrich_py_keywords: bool = False,
):
    """
    Gather keyword definitions from imported downloaded libraries and show progress

    Will only resolve libraries that are actually imported in an in-scope .robot or .resource file.
    """
    reporter.on_get_downloaded_keyword_definitions_start(file_paths)

    robot_file_paths = [p for p in file_paths if p.suffix in (".resource", ".robot")]

    visitor = RobotVisitorLibraryImports(enrich_py_keywords=enrich_py_keywords)
    visit_robot_files(robot_file_paths, visitor)
    downloaded_libraries = list(visitor.downloaded_libraries.values())

    reporter.on_get_downloaded_keyword_definitions_end(file_paths, downloaded_libraries)
    return downloaded_libraries
