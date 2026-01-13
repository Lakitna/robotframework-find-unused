from pathlib import Path

import click

from robotframework_find_unused.common.const import (
    DONE_MARKER,
    INDENT,
    VERBOSE_NO,
    VERBOSE_SINGLE,
    FileUseData,
)
from robotframework_find_unused.common.normalize import normalize_file_path
from robotframework_find_unused.common.visit import visit_robot_files
from robotframework_find_unused.visitors.file_import import FileImportVisitor


def cli_step_parse_file_use(file_paths: list[Path], *, verbose: int):
    """
    Parse files and keep the user up-to-date on progress
    """
    click.echo("Parsing file imports...")

    files = _count_file_uses(file_paths)

    _log_file_stats(files, verbose)
    return files


def _count_file_uses(file_paths: list[Path]) -> list[FileUseData]:
    """
    Walk through all robot files to keep track of imports.
    """
    visitor = FileImportVisitor()
    visit_robot_files(
        file_paths,
        visitor,
        parse_sections=["settings"],
    )
    files = visitor.files

    # Add undiscovered files from input file paths
    for path in file_paths:
        path_normalized = normalize_file_path(path)
        if path_normalized in files:
            continue

        files[path_normalized] = FileUseData(
            id=path_normalized,
            path_absolute=path,
            type=set(),
            used_by=[],
        )

    return list(files.values())


def _log_file_stats(files: list[FileUseData], verbose: int) -> None:
    """
    Output details on parsed files to the user
    """
    click.echo(f"{DONE_MARKER} Parsed {len(files)} files")

    if verbose == VERBOSE_NO:
        return

    file_types: dict[str, list[str]] = {}
    for file in files:
        file_type = "UNKNOWN" if len(file.type) == 0 else next(iter(file.type))

        if file_type not in file_types:
            file_types[file_type] = []
        file_types[file_type].append(file.id)

    for file_type, file_paths in sorted(file_types.items(), key=lambda x: len(x[1]), reverse=True):
        click.echo(f"{INDENT}{len(file_paths)} files of type {file_type}")

        if verbose == VERBOSE_SINGLE:
            continue

        sorted_file_paths = sorted(file_paths, key=lambda f: f)
        for path in sorted_file_paths:
            click.echo(f"{INDENT}{INDENT}{click.style(path, fg='bright_black')}")
