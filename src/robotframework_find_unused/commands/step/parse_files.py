from pathlib import Path

from robot.libdocpkg.model import LibraryDoc

from robotframework_find_unused.parse.libdoc import parse_files_with_libdoc
from robotframework_find_unused.reporter.base.partial.parse_files import (
    PartialReporter_ParseFiles,
)


def step_step_parse_files_with_libdoc(
    file_paths: list[Path],
    *,
    reporter: PartialReporter_ParseFiles,
) -> list[LibraryDoc]:
    """
    Parse files with libdoc and keep the user up-to-date on progress
    """
    reporter.on_parse_files_start(file_paths)

    (parsed_files, errors) = parse_files_with_libdoc(file_paths)

    reporter.on_parse_files_end(file_paths, parsed_files, errors)
    return parsed_files
