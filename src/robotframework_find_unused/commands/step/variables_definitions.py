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

    return visitor.variables


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
