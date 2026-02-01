from pathlib import Path
from typing import cast

from robot.libdocpkg.model import LibraryDoc

from robotframework_find_unused.visitors.python import visit_python_files
from robotframework_find_unused.visitors.python.keyword_visitor import (
    EnrichedKeywordDoc,
    PythonKeywordVisitor,
)


def enrich_python_keyword_data(libdoc: LibraryDoc) -> list[EnrichedKeywordDoc]:
    """Gather data on Python keyword returns"""
    source_path = Path(cast(str, libdoc.source))

    visitor = PythonKeywordVisitor(libdoc.keywords)
    visit_python_files([source_path], visitor)

    return visitor.keywords
