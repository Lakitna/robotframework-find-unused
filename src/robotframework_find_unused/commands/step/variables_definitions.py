from pathlib import Path

import click

from robotframework_find_unused.common.const import (
    DONE_MARKER,
    ERROR_MARKER,
    INDENT,
    VERBOSE_NO,
    VERBOSE_SINGLE,
    VariableData,
)
from robotframework_find_unused.common.normalize import normalize_variable_name
from robotframework_find_unused.common.parse import resolve_variable_name
from robotframework_find_unused.common.visit import visit_robot_files
from robotframework_find_unused.visitors.variable_definition import VariableDefinitionVisitor


def cli_get_variable_definitions(
    file_paths: list[Path],
    *,
    verbose: int,
):
    """
    Walk through all robot files to discover non-local variable definitions and show progress
    """
    click.echo("Gathering variables definitions...")
    variables = _get_variable_definitions(file_paths)

    _log_variable_stats(list(variables.values()), verbose)
    return variables


def _get_variable_definitions(file_paths: list[Path]) -> dict[str, VariableData]:
    """
    Walk through all robot files to discover non-local variable definitions.
    """
    visitor = VariableDefinitionVisitor()
    visit_robot_files(file_paths, visitor)

    return _resolve_vars_in_var_name(visitor.variables)


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


def _log_variable_stats(variables: list[VariableData], verbose: int) -> None:
    """
    Output details to the user
    """
    click.echo(
        (ERROR_MARKER if len(variables) == 0 else DONE_MARKER)
        + f" Found {len(variables)} unique non-local variables definitions",
    )

    if verbose == VERBOSE_NO:
        return

    var_types: dict[str, list[str]] = {}
    for var in variables:
        if var.defined_in_type not in var_types:
            var_types[var.defined_in_type] = []
        var_types[var.defined_in_type].append(var.name)

    for defined_in_type, var_names in sorted(
        var_types.items(),
        key=lambda items: len(items[1]),
        reverse=True,
    ):
        click.echo(f"{INDENT}{len(var_names)} variables definitions of type '{defined_in_type}'")

        if verbose == VERBOSE_SINGLE:
            continue
        for name in var_names:
            click.echo(f"{INDENT}{INDENT}{click.style(name, fg='bright_black')}")
