from pathlib import Path
from typing import TYPE_CHECKING

from .partial.discover_files import PartialReporter_DiscoverFiles

if TYPE_CHECKING:
    from robotframework_find_unused.commands.files import FileOptions
    from robotframework_find_unused.common.const import FileUseData


class FileReporter(PartialReporter_DiscoverFiles):
    """
    Base reporter class for files command.
    """

    def __init__(self, options: "FileOptions") -> None:
        self.options = options

    def on_command_start(self):
        """Before the command does anything"""

    def on_command_end(self, files: list["FileUseData"]):
        """When the command has done all the things"""

    def on_count_file_uses_start(self, file_paths: list[Path], source_path: Path):
        """Before finding out which files are used"""

    def on_count_file_uses_end(
        self,
        file_paths: list[Path],
        source_path: Path,
        files: list["FileUseData"],
    ):
        """When done counting file uses"""

    def on_error(self, error: Exception):
        """When an error is raised"""

    def on_warn(self, warning: str):
        """When an warning is issues"""

    def on_exit(self, reason: str | None, code: int = 0):
        """When the command is done"""
