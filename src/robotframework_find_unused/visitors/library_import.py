from robocop.checkers import VisitorChecker
from robocop.utils import normalize_robot_name
from robot.api.parsing import LibraryImport
from robot.libdoc import LibraryDocumentation
from robot.libdocpkg.model import LibraryDoc

from robotframework_find_unused.common.const import LibraryData
from robotframework_find_unused.common.convert import libdoc_keyword_to_keyword_data


class LibraryImportVisitor(VisitorChecker):
    """
    A Robocop visitor. Will never log a lint issue, unlike a normal Robocop visitor. We use it here
    as a convenient way of working with Robotframework files.

    Uses file exclusion from the Robocop config.

    Gathers downloaded library imports
    """

    downloaded_libraries: dict[str, LibraryData] = {}

    def visit_LibraryImport(self, node: LibraryImport):
        lib_name = node.name

        if lib_name.endswith(".py"):
            # Not a downloaded lib. We already discovered this.
            return

        normalized_lib_name = normalize_robot_name(lib_name)

        if normalized_lib_name in self.downloaded_libraries:
            # Already found it
            return

        lib: LibraryDoc = LibraryDocumentation(lib_name)

        keywords = [libdoc_keyword_to_keyword_data(kw, "LIBRARY") for kw in lib.keywords]
        keyword_names_normalized = set([kw.normalized_name for kw in keywords])

        self.downloaded_libraries[normalized_lib_name] = LibraryData(
            name=lib_name,
            name_normalized=normalized_lib_name,
            keywords=keywords,
            keyword_names_normalized=keyword_names_normalized,
        )
