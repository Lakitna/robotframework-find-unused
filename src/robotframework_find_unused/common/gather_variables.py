from pathlib import Path

from robotframework_find_unused.common.const import VariableData
from robotframework_find_unused.visitors.variable_count import VariableCountVisitor
from robotframework_find_unused.visitors.variable_definition import VariableDefinitionVisitor

from .visit import visit_robot_files


def get_variable_definitions(file_paths: list[Path]) -> dict[str, VariableData]:
    """
    Walk through all robot files to discover non-local variable definitions.
    """
    visitor = VariableDefinitionVisitor()
    visit_robot_files(file_paths, visitor)

    return visitor.variables


def count_variable_uses(
    file_paths: list[Path],
    variables: dict[str, VariableData],
) -> list[VariableData]:
    """
    Walk through all robot files with RoboCop to count keyword uses.
    """
    visitor = VariableCountVisitor(variables)
    visit_robot_files(file_paths, visitor)

    return list(visitor.variables.values())
