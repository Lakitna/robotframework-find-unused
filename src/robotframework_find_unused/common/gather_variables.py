from pathlib import Path

from robotframework_find_unused.visitors.variable import VariableVisitor

from .visit import visit_files


def count_variable_uses(file_paths: list[Path]):
    """
    Walk through all robot files with RoboCop to count keyword uses.
    """
    visitor = VariableVisitor()
    visit_files(file_paths, visitor)

    return [v for v in visitor.variables.values() if v.defined_in_variables_section is True]
