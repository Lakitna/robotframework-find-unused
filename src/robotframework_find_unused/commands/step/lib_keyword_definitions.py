from pathlib import Path

import click

from robotframework_find_unused.common.const import (
    DONE_MARKER,
    ERROR_MARKER,
    INDENT,
    VERBOSE_NO,
    WARN_MARKER,
)
from robotframework_find_unused.common.visit import visit_files
from robotframework_find_unused.visitors.library_import import LibraryData, LibraryImportVisitor


def cli_step_get_downloaded_lib_keywords(
    file_paths: list[Path],
    *,
    verbose: int,
    enrich_py_keywords: bool = False,
):
    """
    Gather keyword definitions from imported downloaded libraries and show progress

    Will only resolve libraries that are actually imported in an in-scope .robot or .resource file.
    """
    click.echo("Gathering downloaded library keyword definitions...")

    robot_file_paths = [p for p in file_paths if p.suffix in (".resource", ".robot")]

    visitor = LibraryImportVisitor(enrich_py_keywords=enrich_py_keywords)
    visit_files(robot_file_paths, visitor)
    downloaded_library = list(visitor.downloaded_libraries.values())

    _log_downloaded_lib_stats(downloaded_library, verbose)
    return downloaded_library


def _log_downloaded_lib_stats(libraries: list[LibraryData], verbose: int) -> None:
    """
    Output details encountered downloaded libraries to the user
    """
    click.echo(
        (WARN_MARKER if len(libraries) == 0 else DONE_MARKER)
        + f" Found {len(libraries)} downloaded libraries",
    )

    if verbose == VERBOSE_NO:
        return

    for lib in libraries:
        if len(lib.keywords) == 0:
            # Import error
            click.echo(f"{INDENT}{lib.name}: {ERROR_MARKER}")
        else:
            click.echo(f"{INDENT}{lib.name}: {len(lib.keywords)} keywords")
