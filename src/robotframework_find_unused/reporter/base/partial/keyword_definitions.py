from pathlib import Path
from typing import TYPE_CHECKING

import robot.errors
from robot.libdocpkg.model import LibraryDoc

from robotframework_find_unused.common.const import KeywordData, LibraryData

if TYPE_CHECKING:
    from robotframework_find_unused.commands.keywords.options import KeywordOptions
    from robotframework_find_unused.commands.returns.options import ReturnOptions


class PartialReporter_CustomKeywordDefinitions:  # noqa: N801
    """
    Partial base reporter for discovering custom keyword definitions.
    """

    def __init__(self, options: "KeywordOptions | ReturnOptions") -> None:
        self.options = options

    def on_get_custom_keyword_definitions_start(self, files: list[LibraryDoc]):
        """Before custom keyword definitions are discovered"""

    def on_get_custom_keyword_definitions_end(
        self,
        files: list[LibraryDoc],
        keywords: list[KeywordData],
    ):
        """After all custom keyword definitions have been discovered"""


class PartialReporter_DownloadedKeywordDefinitions:  # noqa: N801
    """
    Partial base reporter for discovering downloaded keyword definitions.
    """

    def __init__(self, options: "KeywordOptions | ReturnOptions") -> None:
        self.options = options

    def on_get_downloaded_keyword_definitions_start(self, file_paths: list[Path]):
        """Before downloaded (library) keyword definitions are discovered"""

    def on_get_downloaded_keyword_definitions_end(
        self,
        file_paths: list[Path],
        libraries: list[LibraryData],
    ):
        """After all downloaded (library) keyword definitions have been discovered"""

    def on_library_parse_error(
        self,
        error: robot.errors.DataError,
        lib_name: str,
    ):
        """When parsing a library fails"""
