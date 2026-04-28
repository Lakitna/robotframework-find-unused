from pathlib import Path

from robotframework_find_unused.common.const import VariableData
from robotframework_find_unused.reporter.base.variable_reporter import VariableReporter
from robotframework_find_unused.visitors.robot import visit_robot_files
from robotframework_find_unused.visitors.robot.variable_count import RobotVisitorVariableUses


def step_count_variable_uses(
    file_paths: list[Path],
    variable_defs: dict[str, VariableData],
    *,
    reporter: VariableReporter,
):
    """
    Walk through all robot files to count keyword uses and show progress
    """
    reporter.on_count_variable_uses_start(file_paths, variable_defs)

    visitor = RobotVisitorVariableUses(variable_defs)
    visit_robot_files(file_paths, visitor)

    variables = list(visitor.variables.values())

    reporter.on_count_variable_uses_end(file_paths, variable_defs, variables)
    return variables
