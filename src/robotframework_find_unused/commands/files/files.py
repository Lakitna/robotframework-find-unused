"""
Implementation of the 'files' command
"""

from pathlib import Path
from typing import TYPE_CHECKING

from robotframework_find_unused.commands.step.discover_files import step_discover_file_paths
from robotframework_find_unused.commands.step.parse_file_use import step_step_parse_file_use
from robotframework_find_unused.common.pythonpath import apply_pythonpath

if TYPE_CHECKING:
    from robotframework_find_unused.reporter.base.file_reporter import FileReporter

    from .options import FileOptions


def command_files(options: "FileOptions", reporter: "FileReporter") -> None:
    """
    Entry point for the CLI command 'files'
    """
    reporter.on_command_start()

    apply_pythonpath(options.pythonpath)

    file_paths = step_discover_file_paths(options.source_path, reporter=reporter)
    if file_paths is None:
        return

    files = step_step_parse_file_use(
        file_paths,
        Path(options.source_path),
        reporter=reporter,
    )

    reporter.on_command_end(files)
