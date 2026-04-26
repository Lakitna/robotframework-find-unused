import fnmatch
import sys
from pathlib import Path

import click
import robot.errors

from robotframework_find_unused.common.cli import pretty_variable
from robotframework_find_unused.common.const import (
    DONE_MARKER,
    ERROR_MARKER,
    INDENT,
    NOTE_MARKER,
    VERBOSE_NO,
    VERBOSE_SINGLE,
    VariableData,
)
from robotframework_find_unused.reporter.base.variable_reporter import VariableReporter

from .partial.discover_files import PartialCliReporterDiscoverFiles


class VariableCliReporter(VariableReporter, PartialCliReporterDiscoverFiles):
    """
    CLI reporter for variable command.
    """

    def on_get_variable_definitions_start(
        self,
        file_paths: list[Path],
        source_path: Path,
    ):
        click.echo("Gathering variables definitions...")

    def on_get_variable_definitions_end(
        self,
        file_paths: list[Path],
        source_path: Path,
        variables: dict[str, VariableData],
    ):
        if len(variables) == 0:
            click.echo(
                f"{ERROR_MARKER} Found {len(variables)} unique non-local variables definitions",
            )
            if self.options.verbose == VERBOSE_NO:
                click.echo(
                    f"{NOTE_MARKER} Run with `--verbose --verbose` or `-vv` for more details",
                )
            sys.exit(255)
            return

        click.echo(f"{DONE_MARKER} Found {len(variables)} unique non-local variables definitions")

        if self.options.verbose == VERBOSE_NO:
            return

        var_types: dict[str, list[str]] = {}
        for var in variables.values():
            if var.defined_in_type not in var_types:
                var_types[var.defined_in_type] = []
            var_types[var.defined_in_type].append(var.name)

        for defined_in_type, var_names in sorted(
            var_types.items(),
            key=lambda items: len(items[1]),
            reverse=True,
        ):
            click.echo(
                f"{INDENT}{len(var_names)} variables definitions of type '{defined_in_type}'",
            )

            if self.options.verbose == VERBOSE_SINGLE:
                continue
            for name in var_names:
                click.echo(f"{INDENT}{INDENT}{click.style(name, fg='bright_black')}")

    def on_count_variable_uses_start(
        self,
        file_paths: list[Path],
        variables: dict[str, VariableData],
    ):
        click.echo("Counting variable usage...")

    def on_count_variable_uses_end(
        self,
        file_paths: list[Path],
        variables: dict[str, VariableData],
        counted_variables: list[VariableData],
    ):
        total_uses = 0
        for var in counted_variables:
            total_uses += var.use_count

        if total_uses == 0:
            click.echo(
                f"{ERROR_MARKER} Found {total_uses} variable uses of gathered variables",
            )
            if self.options.verbose == VERBOSE_NO:
                click.echo(
                    f"{NOTE_MARKER} Run with `--verbose --verbose` or `-vv` for more details",
                )
            sys.exit(255)
            return

        click.echo(f"{DONE_MARKER} Found {total_uses} variable uses of gathered variables")

        if self.options.verbose == VERBOSE_NO:
            return

        click.echo(f"{INDENT}Variable definitions")
        click.echo(f"{INDENT}{INDENT}Total\t{len(counted_variables)}")

        unused_variables = [var.name for var in counted_variables if var.use_count == 0]
        try:
            percentage_unused = round(len(unused_variables) / len(counted_variables) * 100, 1)
        except ZeroDivisionError:
            percentage_unused = 0

        percentage_used = round((100 - percentage_unused), 1)
        click.echo(
            f"{INDENT}{INDENT}Used\t{len(counted_variables) - len(unused_variables)}\t"
            + click.style(f"({percentage_used}%)", fg="bright_black"),
        )
        click.echo(
            f"{INDENT}{INDENT}Unused\t{len(unused_variables)}\t"
            + click.style(f"({percentage_unused}%)", fg="bright_black"),
        )

        click.echo(f"{INDENT}Variable usage")

        total_uses = 0
        for var in counted_variables:
            total_uses += var.use_count
        click.echo(f"{INDENT}{INDENT}Total\t{total_uses} " + click.style("uses", fg="bright_black"))

        try:
            average = round(total_uses / len(counted_variables), 1)
        except ZeroDivisionError:
            average = 0
        click.echo(
            f"{INDENT}{INDENT}Average\t{average} "
            + click.style("uses per gathered variable", fg="bright_black"),
        )

    def on_command_end(self, counted_variables: list[VariableData]):
        click.echo()

        if self.options.filter_glob:
            click.echo(f"Only showing variables matching pattern '{self.options.filter_glob}'")

            pattern = self.options.filter_glob.lower()
            filtered_variables = []
            for var in counted_variables:
                if fnmatch.fnmatchcase(var.normalized_name, pattern):
                    filtered_variables.append(var)

            counted_variables = filtered_variables

        if self.options.show_all_count:
            sorted_variables = sorted(counted_variables, key=lambda var: var.normalized_name)
            sorted_variables = sorted(sorted_variables, key=lambda var: var.use_count)

            click.echo("use_count\tvariable")
            for var in sorted_variables:
                click.echo("\t".join([str(var.use_count), pretty_variable(var)]))
        else:
            unused_variables = [var for var in counted_variables if var.use_count == 0]
            unused_variables = sorted(unused_variables, key=lambda var: var.normalized_name)

            click.echo(f"Found {len(unused_variables)} unused variables:")
            for var in unused_variables:
                click.echo(INDENT + pretty_variable(var))

        unused_variables = [var for var in counted_variables if var.use_count == 0]
        exit_code = len(unused_variables)
        sys.exit(min(exit_code, 200))

    def on_file_import_error(self, error: Exception, import_str: str, import_from_path: str):
        if isinstance(error, ImportError):
            click.echo(
                f"{ERROR_MARKER} `Variables  {import_str}` <- could not find. "
                f"From {import_from_path}",
            )

        if isinstance(error, robot.errors.DataError):
            click.echo(f"{ERROR_MARKER} {error.message.splitlines()[0]}")
            return

        click.echo(f"{ERROR_MARKER} Failed to import variables from variables file.")
        click.echo(f"{ERROR_MARKER} Something went very wrong. Details below:")
        click.echo(f"{ERROR_MARKER} {error}")
        click.echo()
