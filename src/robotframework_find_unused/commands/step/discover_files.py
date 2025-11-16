import os
from pathlib import Path

import click
from robocop.config import ConfigManager, FileFiltersOptions

from robotframework_find_unused.common.const import (
    DONE_MARKER,
    ERROR_MARKER,
    INDENT,
    NOTE_MARKER,
    VERBOSE_NO,
    VERBOSE_SINGLE,
)


def cli_discover_file_paths(input_path: str, *, verbose: int) -> list[Path]:
    """
    Get file paths recursively with Robocop excludes.
    """
    click.echo(f"Discovering files in `{input_path}` using Robocop config...")

    robocop_config = ConfigManager(sources=[input_path])

    extensions = {"*.robot", "*.resource", "*.py"}
    if robocop_config.default_config.file_filters:
        robocop_config.default_config.file_filters.default_include = extensions
    else:
        robocop_config.default_config.file_filters = FileFiltersOptions(default_include=extensions)

    file_paths = [path[0] for path in robocop_config.paths]

    _log_file_stats(file_paths, input_path, verbose)
    return file_paths


def _log_file_stats(file_paths: list[Path], input_path: str, verbose: int) -> None:
    """
    Output details to the user
    """
    if len(file_paths) == 0:
        click.echo(f"{ERROR_MARKER} Found 0 files in `{input_path}`")
        click.echo(f"{NOTE_MARKER} All files in Robocop config `exclude` are ignored")
        click.echo(f"{NOTE_MARKER} All files listed in `.gitignore` files are ignored")

        if verbose == VERBOSE_NO:
            return

        click.echo(f"{NOTE_MARKER} All of the following files are excluded:")
        for root, _dirs, files in os.walk(input_path):
            for file in files:
                click.echo(f"{INDENT}{Path(root, file).as_posix()}")
        return

    if verbose == VERBOSE_NO:
        return

    click.echo(f"{DONE_MARKER} Discovered {len(file_paths)} files")

    if verbose == VERBOSE_SINGLE:
        return

    for path in file_paths:
        click.echo(INDENT + click.style(str(path), fg="bright_black"))
