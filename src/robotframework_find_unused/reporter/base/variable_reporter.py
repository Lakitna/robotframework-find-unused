from pathlib import Path
from typing import TYPE_CHECKING

from robotframework_find_unused.common.const import VariableData

from .partial.discover_files import PartialReporter_DiscoverFiles

if TYPE_CHECKING:
    from robotframework_find_unused.commands.variables import VariableOptions


class VariableReporter(PartialReporter_DiscoverFiles):
    """
    Base reporter class for variable command.
    """

    def __init__(self, options: "VariableOptions") -> None:
        self.options = options

    def on_command_start(self):
        """Before the command does anything"""

    def on_command_end(self, counted_variables: list[VariableData]):
        """When the command has done all the things"""

    def on_get_variable_definitions_start(
        self,
        file_paths: list[Path],
        source_path: Path,
    ):
        """Before variable definitions are discovered"""

    def on_get_variable_definitions_end(
        self,
        file_paths: list[Path],
        source_path: Path,
        variables: dict[str, VariableData],
    ):
        """After variable definitions are discovered"""

    def on_count_variable_uses_start(
        self,
        file_paths: list[Path],
        variables: dict[str, VariableData],
    ):
        """Before variable uses are counted"""

    def on_count_variable_uses_end(
        self,
        file_paths: list[Path],
        variables: dict[str, VariableData],
        counted_variables: list[VariableData],
    ):
        """After variable uses are counted"""
