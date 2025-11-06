from typing import TYPE_CHECKING

from robocop.checkers import VisitorChecker
from robocop.utils import normalize_robot_name
from robot.api.parsing import LibraryImport
from robot.libdoc import LibraryDocumentation

from robotframework_find_unused.common.const import LibraryData
from robotframework_find_unused.common.convert import libdoc_keyword_to_keyword_data

if TYPE_CHECKING:
    from robot.libdocpkg.model import LibraryDoc


class LibraryImportVisitor(VisitorChecker):
    """
    Gather downloaded library imports

    A Robocop visitor. Will never log a lint issue, unlike a normal Robocop visitor. We use it here
    as a convenient way of working with Robotframework files.

    Uses file exclusion from the Robocop config.
    """

    downloaded_libraries: dict[str, LibraryData]

    def __init__(self) -> None:
        self.downloaded_libraries = {}
        super().__init__()

        # Is always imported automatically by Robot
        self._register_downloaded_library("BuiltIn")

    def visit_LibraryImport(self, node: LibraryImport):  # noqa: N802
        """Find out which libraries are actually used"""
        lib_name = node.name

        if lib_name.endswith(".py"):
            # Not a downloaded lib. We already discovered this.
            return

        self._register_downloaded_library(lib_name)

    def _register_downloaded_library(self, lib_name: str) -> None:
        normalized_lib_name = normalize_robot_name(lib_name)

        if normalized_lib_name in self.downloaded_libraries:
            # Already found it
            return

        lib: LibraryDoc = LibraryDocumentation(lib_name)

        keywords = [libdoc_keyword_to_keyword_data(kw, "LIBRARY") for kw in lib.keywords]
        keyword_names_normalized = {kw.normalized_name for kw in keywords}

        self.downloaded_libraries[normalized_lib_name] = LibraryData(
            name=lib_name,
            name_normalized=normalized_lib_name,
            keywords=keywords,
            keyword_names_normalized=keyword_names_normalized,
        )
