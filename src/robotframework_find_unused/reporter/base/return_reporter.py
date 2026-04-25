from typing import TYPE_CHECKING

from robotframework_find_unused.common.const import KeywordData

from .partial.count_keywords import PartialReporter_CountKeywords
from .partial.discover_files import PartialReporter_DiscoverFiles
from .partial.keyword_definitions import (
    PartialReporter_CustomKeywordDefinitions,
    PartialReporter_DownloadedKeywordDefinitions,
)
from .partial.parse_files import PartialReporter_ParseFiles

if TYPE_CHECKING:
    from robotframework_find_unused.commands.returns import ReturnOptions


class ReturnReporter(
    PartialReporter_DiscoverFiles,
    PartialReporter_ParseFiles,
    PartialReporter_CustomKeywordDefinitions,
    PartialReporter_DownloadedKeywordDefinitions,
    PartialReporter_CountKeywords,
):
    """
    Base reporter class for return command.
    """

    def __init__(self, options: "ReturnOptions") -> None:
        self.options = options

    def on_command_start(self):
        """Before the command does anything"""

    def on_command_end(self, counted_keywords: list[KeywordData]):
        """When the command has done all the things"""
