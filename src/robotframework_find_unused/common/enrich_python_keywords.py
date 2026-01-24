import ast
from pathlib import Path
from typing import cast

from robot.libdocpkg.model import LibraryDoc

from robotframework_find_unused.visitors.python_keyword_visitor import (
    EnrichedKeywordDoc,
    PythonKeywordVisitor,
)


def enrich_python_keyword_data(libdoc: LibraryDoc) -> list[EnrichedKeywordDoc]:
    """Gather data on Python keyword returns"""
    source_path = Path(cast(str, libdoc.source))
    with source_path.open(encoding="utf8") as f:
        raw_python_source = f.read()
    model = ast.parse(raw_python_source)

    visitor = PythonKeywordVisitor(libdoc.keywords)
    visitor.visit(model)

    return visitor.keywords
