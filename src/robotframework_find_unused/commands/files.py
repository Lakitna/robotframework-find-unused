"""
Implementation of the 'files' command
"""

from typing import Literal, Optional
from pathlib import Path
from dataclasses import dataclass

import click

from robotframework_find_unused.common.cli import cli_hard_exit
from robotframework_find_unused.common.const import WARN_MARKER, INDENT, FileUseData, FileUseType
from robotframework_find_unused.common.normalize import normalize_file_path

from .step.discover_files import cli_discover_file_paths
from .step.parse_file_use import cli_step_parse_file_use


@dataclass
class FileOptions:
    """
    Command line options for the 'files' command
    """

    path_filter_glob: str | None
    show_all_count: bool
    verbose: int
    source_path: str


def cli_files(options: FileOptions):
    """
    Entry point for the CLI command
    """
    file_paths = cli_discover_file_paths(options.source_path, verbose=options.verbose)
    if len(file_paths) == 0:
        return cli_hard_exit(options.verbose)

    files = cli_step_parse_file_use(file_paths, verbose=options.verbose)

    return 0
