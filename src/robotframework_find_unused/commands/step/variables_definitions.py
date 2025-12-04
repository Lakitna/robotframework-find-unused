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
from robotframework_find_unused.common.gather_variables import get_variable_definitions


def cli_get_variable_definitions(
    file_paths: list[Path],
    *,
    verbose: int,
):
    """
    Gather variable definitions and count variable uses and show progress
    """
    click.echo("Gathering variables definitions...")
    variables = get_variable_definitions(file_paths)

    _log_variable_stats(list(variables.values()), verbose)
    return variables


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
        click.echo(f"{INDENT}{len(var_names)} variables defined in {defined_in_type}")

        if verbose == VERBOSE_SINGLE:
            continue
        for name in var_names:
            click.echo(f"{INDENT}{INDENT}{click.style(name, fg='bright_black')}")
