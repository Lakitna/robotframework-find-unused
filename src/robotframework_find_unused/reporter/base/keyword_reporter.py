from pathlib import Path
from typing import TYPE_CHECKING

from robotframework_find_unused.common.const import (
    DONE_MARKER,
    ERROR_MARKER,
    INDENT,
    NOTE_MARKER,
    VERBOSE_DOUBLE,
    VERBOSE_NO,
    VERBOSE_SINGLE,
    WARN_MARKER,
    FileUseData,
    FileUsedByData,
    KeywordData,
)
from robotframework_find_unused.visitors.robot.library_import import (
    LibraryData,
    RobotVisitorLibraryImports,
)

from .partial.discover_files import PartialBaseReporterDiscoverFiles

if TYPE_CHECKING:
    from robotframework_find_unused.commands.keywords import KeywordOptions
from robot.libdocpkg.model import LibraryDoc


class KeywordReporter(PartialBaseReporterDiscoverFiles):
    """
    Base reporter class for keyword command.
    """

    def __init__(self, options: "KeywordOptions") -> None:
        self.options = options

    def on_command_start(self):
        """Before the command does anything"""

    def on_command_end(self, counted_keywords: list[KeywordData]):
        """When the command has done all the things"""

    def on_parse_files_start(self, file_paths: list[Path]):
        """Before Libdoc file parsing starts"""

    def on_parse_files_end(
        self,
        file_paths: list[Path],
        files: list[LibraryDoc],
        parse_errors: list[str],
    ):
        """After all files have been parsed by Libdoc"""

    def on_get_custom_keyword_definitions_start(self, files: list[LibraryDoc]):
        """Before custom keyword definitions are discovered"""

    def on_get_custom_keyword_definitions_end(
        self,
        files: list[LibraryDoc],
        keywords: list[KeywordData],
    ):
        """After all custom keyword definitions have been discovered"""

    def on_get_downloaded_keyword_definitions_start(self, file_paths: list[Path]):
        """Before downloaded (library) keyword definitions are discovered"""

    def on_get_downloaded_keyword_definitions_end(
        self,
        file_paths: list[Path],
        libraries: list[LibraryData],
    ):
        """After all downloaded (library) keyword definitions have been discovered"""

    def on_count_keyword_uses_start(
        self,
        file_paths: list[Path],
        keywords: list[KeywordData],
        downloaded_libraries: list[LibraryData],
    ):
        """Before keyword uses are counted"""

    def on_count_keyword_uses_end(
        self,
        file_paths: list[Path],
        keywords: list[KeywordData],
        downloaded_libraries: list[LibraryData],
        counted_keywords: list[KeywordData],
    ):
        """After keyword uses are counted"""

    # def on_error(self, error: Exception):
    #     """When an error is raised"""

    # def on_warn(self, warning: str):
    #     """When an warning is issues"""

    # def on_exit(self, reason: str | None, code: int = 0):
    #     """When the command is done"""
