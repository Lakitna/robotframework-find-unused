from pathlib import Path

import click

from robotframework_find_unused.common.const import (
    DONE_MARKER,
    ERROR_MARKER,
    INDENT,
    VERBOSE_NO,
    VariableData,
)
from robotframework_find_unused.common.visit import visit_robot_files
from robotframework_find_unused.visitors.variable_count import VariableCountVisitor


def cli_count_variable_uses(
    file_paths: list[Path],
    variable_defs: dict[str, VariableData],
    *,
    verbose: int,
):
    """
    Walk through all robot files with RoboCop to count keyword uses and show progress
    """
    click.echo("Counting variable usage...")
    variables = _count_variable_uses(file_paths, variable_defs)

    _log_variable_stats(variables, verbose)
    return variables


def _count_variable_uses(
    file_paths: list[Path],
    variables: dict[str, VariableData],
) -> list[VariableData]:
    """
    Walk through all robot files with RoboCop to count keyword uses.
    """
    visitor = VariableCountVisitor(variables)
    visit_robot_files(file_paths, visitor)

    return list(visitor.variables.values())


def _log_variable_stats(variables: list[VariableData], verbose: int) -> None:
    """
    Output details encountered downloaded libraries to the user
    """
    total_uses = 0
    for var in variables:
        total_uses += var.use_count
    click.echo(
        (ERROR_MARKER if total_uses == 0 else DONE_MARKER)
        + f" Found {total_uses} variable uses of gathered variables",
    )

    if verbose == VERBOSE_NO:
        return

    click.echo(f"{INDENT}Variable definitions")
    click.echo(f"{INDENT}{INDENT}Total\t{len(variables)}")

    unused_variables = [var.name for var in variables if var.use_count == 0]
    try:
        percentage_unused = round(len(unused_variables) / len(variables) * 100, 1)
    except ZeroDivisionError:
        percentage_unused = 0

    percentage_used = round((100 - percentage_unused), 1)
    click.echo(
        f"{INDENT}{INDENT}Used\t{len(variables) - len(unused_variables)}\t"
        + click.style(f"({percentage_used}%)", fg="bright_black"),
    )
    click.echo(
        f"{INDENT}{INDENT}Unused\t{len(unused_variables)}\t"
        + click.style(f"({percentage_unused}%)", fg="bright_black"),
    )

    click.echo(f"{INDENT}Variable usage")

    total_uses = 0
    for var in variables:
        total_uses += var.use_count
    click.echo(f"{INDENT}{INDENT}Total\t{total_uses} " + click.style("uses", fg="bright_black"))

    try:
        average = round(total_uses / len(variables), 1)
    except ZeroDivisionError:
        average = 0
    click.echo(
        f"{INDENT}{INDENT}Average\t{average} "
        + click.style("uses per gathered variable", fg="bright_black"),
    )
