"""
Implementation of the 'variables' command
"""

import fnmatch
from dataclasses import dataclass

import click

from robotframework_find_unused.commands.step.discover_files import cli_discover_file_paths
from robotframework_find_unused.commands.step.variables_count_uses import cli_count_variable_uses
from robotframework_find_unused.common.cli import cli_hard_exit
from robotframework_find_unused.common.const import INDENT, VariableData


@dataclass
class VariableOptions:
    """
    Command line options for the 'variables' command
    """

    show_all_count: bool
    filter_glob: str | None
    verbose: int
    source_path: str


def cli_variables(options: VariableOptions):
    """
    Entry point for the CLI command
    """
    file_paths = cli_discover_file_paths(options.source_path, verbose=options.verbose)
    if len(file_paths) == 0:
        return cli_hard_exit(options.verbose)

    variables = cli_count_variable_uses(
        file_paths,
        verbose=options.verbose,
    )
    if len(variables) == 0:
        return cli_hard_exit(options.verbose)

    _cli_log_results(variables, options)
    return _exit_code(variables)


def _cli_log_results(variables: list[VariableData], options: VariableOptions) -> None:
    click.echo()

    if options.filter_glob:
        click.echo(f"Only showing variables matching pattern '{options.filter_glob}'")

        pattern = options.filter_glob.lower()
        filtered_variables = []
        for var in variables:
            if fnmatch.fnmatchcase(var.name_without_brackets.lower(), pattern):
                filtered_variables.append(var)

        variables = filtered_variables

    if options.show_all_count:
        sorted_variables = sorted(variables, key=lambda var: var.normalized_name)
        sorted_variables = sorted(sorted_variables, key=lambda var: var.use_count)

        click.echo("use_count\tvariable")
        for var in sorted_variables:
            click.echo("\t".join([str(var.use_count), var.name]))
    else:
        unused_variables = [var for var in variables if var.use_count == 0]
        unused_variables = sorted(unused_variables, key=lambda var: var.normalized_name)

        click.echo(f"Found {len(unused_variables)} unused variables:")
        for var in unused_variables:
            click.echo(INDENT + var.name)


def _exit_code(variables: list[VariableData]) -> int:
    unused_variables = [var for var in variables if var.use_count == 0]
    exit_code = len(unused_variables)
    return min(exit_code, 200)
