from pathlib import Path

import click
from robot.libdocpkg.model import LibraryDoc

from robotframework_find_unused.common.const import (
    VERBOSE_NO,
    VERBOSE_SINGLE,
)
from robotframework_find_unused.reporter.base.partial.parse_files import (
    PartialReporter_ParseFiles,
)
from robotframework_find_unused.reporter.cli.common import (
    DONE,
    INDENT,
    WARN,
)


class PartialCliReporterParseFiles(PartialReporter_ParseFiles):
    """
    Partial CLI reporter for pasring files.
    """

    def on_parse_files_start(self, file_paths: list[Path]):
        click.echo("Parsing files with LibDoc...")

    def on_parse_files_end(
        self,
        file_paths: list[Path],
        files: list[LibraryDoc],
        parse_errors: list[str],
    ):
        """After all files have been parsed by Libdoc"""
        if len(parse_errors) > 0:
            click.echo(
                f"{WARN} Failed to parse {len(parse_errors)} files. Files will be ignored",
            )
            for error in parse_errors:
                click.echo(f"{INDENT}{WARN} {error}")

        click.echo(f"{DONE} Parsed {len(files)} files")

        if self.options.verbose == VERBOSE_NO:
            return

        file_types: dict[str, list[str]] = {}
        for file in files:
            if not file.source:
                continue

            if file.type not in file_types:
                file_types[file.type] = []
            file_types[file.type].append(file.source)

        for file_type, paths in sorted(file_types.items(), key=lambda x: len(x[1]), reverse=True):
            click.echo(f"{INDENT}{len(paths)} files of type CUSTOM_{file_type}")

            if self.options.verbose == VERBOSE_SINGLE:
                continue
            for path in paths:
                click.echo(f"{INDENT}{INDENT}{click.style(path, fg='bright_black')}")
