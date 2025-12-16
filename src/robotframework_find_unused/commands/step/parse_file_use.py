from pathlib import Path

import click

from robotframework_find_unused.common.const import (
    DONE_MARKER,
    INDENT,
    VERBOSE_NO,
    VERBOSE_SINGLE,
    WARN_MARKER,
    FileUseData,
)
from robotframework_find_unused.common.visit import visit_robot_files
from robotframework_find_unused.common.normalize import normalize_file_path
from robotframework_find_unused.visitors.file_import import FileImportVisitor


def cli_step_parse_file_use(file_paths: list[Path], *, verbose: int):
    """
    Parse files with libdoc and keep the user up-to-date on progress
    """
    click.echo("Parsing file imports...")

    files = _count_file_uses(file_paths)

    return files


def _count_file_uses(file_paths: list[Path]) -> list[FileUseData]:
    """
    Walk through all robot files to keep track of imports.
    """
    visitor = FileImportVisitor()
    visit_robot_files(file_paths, visitor)
    files = visitor.files

    # Add undiscovered files from input file paths
    for path in file_paths:
        path_normalized = path.as_posix()
        if path_normalized in files:
            continue

        files[path_normalized] = FileUseData(
            id=normalize_file_path(path),
            path_absolute=path,
            type=set(),
            used_by=[],
        )

    return list(files.values())
