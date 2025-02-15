"""
Implementation of the 'variables' command
"""

import fnmatch
from dataclasses import dataclass

import click
from robocop import Config

from robotframework_find_unused.common.cli import cli_count_variable_uses
from robotframework_find_unused.common.const import VariableData


@dataclass
class VariableOptions:
    """
    Command line options for the 'variables' command
    """

    show_all_count: bool
    filter_glob: str | None
    verbose: bool


def cli_variables(file_path: str, option: VariableOptions):
    """
    Entry point for the CLI command
    """
    robocop_config = Config()
    robocop_config.paths = [file_path]

    variables = cli_count_variable_uses(robocop_config, verbose=option.verbose)

    _cli_log_results(variables, option)


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
            click.echo("  " + name)

        click.echo()
        click.echo(f"Found {len(unused_variables)} unused variables")
