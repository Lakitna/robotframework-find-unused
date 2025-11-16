# pyright: reportPrivateImportUsage=false

from typing import TYPE_CHECKING

import click
import robot.errors
from robocop.linter.utils.misc import normalize_robot_name
from robot.api.parsing import LibraryImport, ModelVisitor
from robot.libdoc import LibraryDocumentation

from robotframework_find_unused.common.const import ERROR_MARKER, LibraryData
from robotframework_find_unused.common.convert import libdoc_keyword_to_keyword_data

if TYPE_CHECKING:
    from robot.libdocpkg.model import LibraryDoc


class LibraryImportVisitor(ModelVisitor):
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

        try:
            lib: LibraryDoc = LibraryDocumentation(lib_name)
        except robot.errors.DataError:
            click.echo(
                f"{ERROR_MARKER} Failed to gather keywords from library `{lib_name}`",
                err=True,
            )

            self.downloaded_libraries[normalized_lib_name] = LibraryData(
                name=lib_name,
                name_normalized=normalized_lib_name,
                keywords=[],
                keyword_names_normalized=set(),
            )
            return

        keywords = [libdoc_keyword_to_keyword_data(kw, "LIBRARY") for kw in lib.keywords]
        keyword_names_normalized = {kw.normalized_name for kw in keywords}

        self.downloaded_libraries[normalized_lib_name] = LibraryData(
            name=lib_name,
            name_normalized=normalized_lib_name,
            keywords=keywords,
            keyword_names_normalized=keyword_names_normalized,
        )
