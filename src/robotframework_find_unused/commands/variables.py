"""
Implementation of the 'variables' command
"""

import fnmatch
import sys
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
    return 0


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
        sorted_variables = sorted(variables, key=lambda var: var.use_count)

        click.echo("use_count\tvariable")
        for var in sorted_variables:
            click.echo("\t".join([str(var.use_count), var.name]))
    else:
        unused_variables = [var.name for var in variables if var.use_count == 0]

        click.echo(f"Found {len(unused_variables)} unused variables:")
        for name in unused_variables:
            click.echo(INDENT + name)
