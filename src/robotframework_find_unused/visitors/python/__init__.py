"""
Python AST visitors
"""

import ast
from pathlib import Path


def visit_python_files(file_paths: list[Path], visitor: ast.NodeVisitor):
    """
    Parse and visit Python files.
    """
    for file_path in file_paths:
        with file_path.open(encoding="utf8") as f:
            raw_python_source = f.read()

        model = ast.parse(raw_python_source)
        visitor.visit(model)
