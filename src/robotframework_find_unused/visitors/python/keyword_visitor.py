import ast

from robot.libdocpkg.model import KeywordDoc

from robotframework_find_unused.common.impossible_state_error import ImpossibleStateError


class EnrichedKeywordDoc:
    """Wrap Libdocs KeywordDoc to add more data."""

    returns: bool | None = None

    def __init__(self, doc: KeywordDoc) -> None:
        self.doc = doc


class PythonKeywordVisitor(ast.NodeVisitor):
    """Visit single Python file AST to find data in functions"""

    def __init__(self, keywords: list[KeywordDoc]) -> None:
        self.keywords: list[EnrichedKeywordDoc] = []
        for keyword in keywords:
            self.keywords.append(EnrichedKeywordDoc(keyword))

    def visit_FunctionDef(self, node: ast.FunctionDef):  # noqa: N802
        """Visit function definition"""
        self._register_function_return(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):  # noqa: N802
        """Visit async function definition"""
        self._register_function_return(node)

    def _register_function_return(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        matching_keywords = [kw for kw in self.keywords if kw.doc.lineno == node.lineno]
        if not matching_keywords:
            # Function is not a keyword
            return

        if len(matching_keywords) > 1:
            msg = "Found multiple Python keyword definitions on the same line"
            raise ImpossibleStateError(msg)

        matching_keyword = matching_keywords[0]

        visitor = PythonKeywordReturnVisitor()
        visitor.visit(node)
        matching_keyword.returns = visitor.has_return_node


class PythonKeywordReturnVisitor(ast.NodeVisitor):
    """Only visit return statements of Python AST."""

    def __init__(self) -> None:
        self.has_return_node: bool = False

    def visit_Return(self, node: ast.Return):  # noqa: N802
        """Visit function return"""
        if self.has_return_node is True:
            return
        self.has_return_node = node.value is not None
