from pathlib import Path

import click

from robotframework_find_unused.common.const import (
    DONE_MARKER,
    ERROR_MARKER,
    INDENT,
    VERBOSE_NO,
    VariableData,
)
from robotframework_find_unused.common.gather_variables import count_variable_uses


def cli_count_variable_uses(
    file_paths: list[Path],
    *,
    verbose: int,
):
    """
    Gather variable definitions and count variable uses and show progress
    """
    click.echo("Gathering variables usage...")
    variables = count_variable_uses(file_paths)
    click.echo(
        (ERROR_MARKER if len(variables) == 0 else DONE_MARKER)
        + f" Found {len(variables)} unique variables defined in a variables section",
    )

    _log_variable_stats(variables, verbose)
    return variables


def _log_variable_stats(variables: list[VariableData], verbose: int) -> None:
    """
    Output details encountered downloaded libraries to the user
    """
    if verbose == VERBOSE_NO:
        return

    click.echo(
        f"{INDENT}{len(variables)}\ttotal variables",
    )

    unused_variables = [var.name for var in variables if var.use_count == 0]
    try:
        percentage = round(len(unused_variables) / len(variables) * 100, 1)
    except ZeroDivisionError:
        percentage = 0
    click.echo(
        f"{INDENT}{len(unused_variables)}\tunused variables ({percentage}%)",
    )

    total_uses = 0
    for var in variables:
        total_uses += var.use_count
    click.echo("Variables section variables usage metrics:")
    click.echo(f"{INDENT}Total\t{total_uses}x")

    try:
        average = round(total_uses / len(variables), 1)
    except ZeroDivisionError:
        average = 0
    click.echo(f"{INDENT}Average\t{average}x per variable")
