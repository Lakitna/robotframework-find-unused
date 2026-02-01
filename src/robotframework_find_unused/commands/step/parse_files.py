from pathlib import Path

import click
from robot.libdocpkg.model import LibraryDoc

from robotframework_find_unused.common.const import (
    DONE_MARKER,
    INDENT,
    VERBOSE_NO,
    VERBOSE_SINGLE,
    WARN_MARKER,
)
from robotframework_find_unused.parse.libdoc import parse_files_with_libdoc


def cli_step_parse_files_with_libdoc(file_paths: list[Path], *, verbose: int) -> list[LibraryDoc]:
    """
    Parse files with libdoc and keep the user up-to-date on progress
    """
    click.echo("Parsing files with LibDoc...")

    (parsed_files, errors) = parse_files_with_libdoc(file_paths)

    _log_file_errors(errors)
    _log_file_stats(parsed_files, verbose)
    return parsed_files


def _log_file_errors(errors: list[str]) -> None:
    if len(errors) == 0:
        return

    click.echo(f"{WARN_MARKER} Failed to parse {len(errors)} files. Files will be ignored")

    for error in errors:
        click.echo(f"{INDENT}{WARN_MARKER} {error}")


def _log_file_stats(files: list[LibraryDoc], verbose: int) -> None:
    """
    Output details on parsed files to the user
    """
    click.echo(f"{DONE_MARKER} Parsed {len(files)} files")

    if verbose == VERBOSE_NO:
        return

    file_types: dict[str, list[str]] = {}
    for file in files:
        if not file.source:
            continue

        if file.type not in file_types:
            file_types[file.type] = []
        file_types[file.type].append(file.source)

    for file_type, file_paths in sorted(file_types.items(), key=lambda x: len(x[1]), reverse=True):
        click.echo(f"{INDENT}{len(file_paths)} files of type CUSTOM_{file_type}")

        if verbose == VERBOSE_SINGLE:
            continue
        for path in file_paths:
            click.echo(f"{INDENT}{INDENT}{click.style(path, fg='bright_black')}")
