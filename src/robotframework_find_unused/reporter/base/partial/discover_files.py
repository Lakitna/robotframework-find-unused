from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from robotframework_find_unused.commands.keywords.options import KeywordOptions
    from robotframework_find_unused.commands.returns.options import ReturnOptions


class PartialReporter_DiscoverFiles:  # noqa: N801
    """
    Partial base reporter for discovering files.
    """

    def __init__(self, options: "KeywordOptions | ReturnOptions") -> None:
        self.options = options

    def on_discover_files_start(self, root_folder: str):
        """Before files to be analyzed are discovered"""

    def on_discover_files_success(self, root_folder: str, discovered_files: list[Path]):
        """When discovering files was a success"""

    def on_discover_files_fail(self, root_folder: str, errors: list[str]):
        """When discovering files fails"""
