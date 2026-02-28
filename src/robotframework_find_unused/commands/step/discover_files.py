import os
from pathlib import Path

import click
import robocop

from robotframework_find_unused.common.const import (
    DONE_MARKER,
    ERROR_MARKER,
    INDENT,
    NOTE_MARKER,
    VERBOSE_DOUBLE,
    VERBOSE_NO,
    VERBOSE_SINGLE,
)

FILE_EXTENSIONS = {"*.robot", "*.resource", "*.py"}


def cli_discover_file_paths(input_path: str, *, verbose: int) -> list[Path]:
    """
    Get file paths recursively with Robocop excludes.
    """
    click.echo(f"Discovering files in `{input_path}` using Robocop config...")

    if robocop.__version__.startswith("6.") or robocop.__version__.startswith("7."):
        file_paths = _discover_file_paths_robocop_6_7(input_path)
    else:
        file_paths = _discover_file_paths_robocop(input_path)

    sorted_file_paths = sorted(file_paths, key=lambda f: f)
    sorted_file_paths = sorted(
        sorted_file_paths,
        key=lambda p: len(p.parts)
        # __init__ files should always be before the files they apply to
        + (-0.5 if p.stem == "__init__" else 0),
    )

    _log_file_stats(sorted_file_paths, input_path, verbose)
    return sorted_file_paths


def _discover_file_paths_robocop_6_7(input_path: str) -> list[Path]:
    """
    Get file paths recursively with Robocop.

    Only works for Robocop 6.x.x and 7.x.x
    """
    from robocop.config import ConfigManager, FileFiltersOptions  # type: ignore  # noqa: PGH003

    robocop_config = ConfigManager(sources=[input_path])

    extensions = FILE_EXTENSIONS
    if robocop_config.default_config.file_filters:
        robocop_config.default_config.file_filters.default_include = extensions
    else:
        robocop_config.default_config.file_filters = FileFiltersOptions(default_include=extensions)

    return [path[0] for path in robocop_config.paths]


def _discover_file_paths_robocop(input_path: str) -> list[Path]:
    """
    Get file paths recursively with Robocop.

    Works for Robocop 8.x.x and up
    """
    from robocop.config.builder import (
        RawConfig,  # type: ignore  # noqa: PGH003
        RawFileFiltersOptions,  # type: ignore  # noqa: PGH003
    )
    from robocop.config.manager import ConfigManager  # type: ignore  # noqa: PGH003

    config_manager = ConfigManager(
        sources=[input_path],
        overwrite_config=RawConfig(
            file_filters=RawFileFiltersOptions(default_include=list(FILE_EXTENSIONS)),
        ),
    )

    return [source_file.path for source_file in config_manager.paths]


def _log_file_stats(file_paths: list[Path], input_path: str, verbose: int) -> None:
    """
    Output details to the user
    """
    if len(file_paths) == 0:
        click.echo(f"{ERROR_MARKER} Found 0 files in `{input_path}`")
        click.echo(f"{NOTE_MARKER} All files in Robocop config `exclude` are ignored")
        click.echo(f"{NOTE_MARKER} All files listed in `.gitignore` files are ignored")

        if verbose < VERBOSE_DOUBLE:
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
