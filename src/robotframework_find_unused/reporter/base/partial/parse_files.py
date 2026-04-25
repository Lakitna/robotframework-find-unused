from pathlib import Path
from typing import TYPE_CHECKING

from robot.libdocpkg.model import LibraryDoc

if TYPE_CHECKING:
    from robotframework_find_unused.commands.keywords import KeywordOptions
    from robotframework_find_unused.commands.returns import ReturnOptions


class PartialReporter_ParseFiles:  # noqa: N801
    """
    Partial base reporter for parsing files.
    """

    def __init__(self, options: "KeywordOptions | ReturnOptions") -> None:
        self.options = options

    def on_parse_files_start(self, file_paths: list[Path]):
        """Before Libdoc file parsing starts"""

    def on_parse_files_end(
        self,
        file_paths: list[Path],
        files: list[LibraryDoc],
        parse_errors: list[str],
    ):
        """After all files have been parsed by Libdoc"""
