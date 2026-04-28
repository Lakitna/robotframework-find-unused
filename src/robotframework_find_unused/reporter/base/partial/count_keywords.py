from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from robotframework_find_unused.commands.keywords.options import KeywordOptions
    from robotframework_find_unused.commands.returns.options import ReturnOptions
    from robotframework_find_unused.common.const import KeywordData, LibraryData


class PartialReporter_CountKeywords:  # noqa: N801
    """
    Partial base reporter for counting keywords.
    """

    def __init__(self, options: "KeywordOptions | ReturnOptions") -> None:
        self.options = options

    def on_count_keyword_uses_start(
        self,
        file_paths: list[Path],
        keywords: "list[KeywordData]",
        downloaded_libraries: "list[LibraryData]",
    ):
        """Before keyword uses are counted"""

    def on_count_keyword_uses_end(
        self,
        file_paths: list[Path],
        keywords: "list[KeywordData]",
        downloaded_libraries: "list[LibraryData]",
        counted_keywords: "list[KeywordData]",
    ):
        """After keyword uses are counted"""

    def on_filter_keywords(
        self,
        keywords: "list[KeywordData]",
        filtered_keywords: "list[KeywordData]",
        descriptor: str,
    ):
        """When keywords are filtered from the output."""
