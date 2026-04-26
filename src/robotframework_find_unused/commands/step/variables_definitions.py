from pathlib import Path

from robotframework_find_unused.common.const import VariableData
from robotframework_find_unused.common.normalize import normalize_variable_name
from robotframework_find_unused.reporter.base.variable_reporter import VariableReporter
from robotframework_find_unused.resolve.resolve_variables import resolve_variable_name
from robotframework_find_unused.visitors.robot import visit_robot_files
from robotframework_find_unused.visitors.robot.variable_definition import (
    RobotVisitorVariableDefinitions,
)


def step_get_variable_definitions(
    file_paths: list[Path],
    source_path: Path,
    *,
    reporter: VariableReporter,
):
    """
    Walk through all robot files to discover non-local variable definitions and show progress
    """
    reporter.on_get_variable_definitions_start(file_paths, source_path)

    visitor = RobotVisitorVariableDefinitions(source_path, set(file_paths))
    visit_robot_files(file_paths, visitor)

    variables = _resolve_vars_in_var_name(visitor.variables)

    reporter.on_get_variable_definitions_end(file_paths, source_path, variables)
    return variables


def _resolve_vars_in_var_name(variables: dict[str, VariableData]) -> dict[str, VariableData]:
    resolved_variables: dict[str, VariableData] = {}
    all_used_vars: list[str] = []
    for var in variables.values():
        var_name = var.normalized_name
        (resolved_var_name, used_vars) = resolve_variable_name(var_name, variables)
        resolved_var_name_normalized = normalize_variable_name(resolved_var_name)

        if resolved_var_name_normalized == var_name:
            # Nothing to resolve
            resolved_variables[var_name] = var
            continue

        resolved_variables[resolved_var_name_normalized] = VariableData(
            name=var.name,
            type=var.type,
            normalized_name=resolved_var_name_normalized,
            resolved_name="${" + resolved_var_name + "}",
            use_count=var.use_count,
            defined_in_type=var.defined_in_type,
            defined_in=var.defined_in,
            value=var.value,
        )

        all_used_vars = all_used_vars + used_vars

    for used_var in all_used_vars:
        if used_var not in resolved_variables:
            continue
        resolved_variables[used_var].use_count += 1

    return resolved_variables
