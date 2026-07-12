import sys
from pathlib import Path

import click
from robot.errors import DataError
from robot.libdocpkg.model import LibraryDoc

from robotframework_find_unused.common.const import (
    VERBOSE_NO,
    VERBOSE_SINGLE,
    KeywordData,
)
from robotframework_find_unused.reporter.base.partial.keyword_definitions import (
    PartialReporter_CustomKeywordDefinitions,
    PartialReporter_DownloadedKeywordDefinitions,
)
from robotframework_find_unused.reporter.cli.common import (
    DONE,
    ERROR,
    INDENT,
    NOTE,
    WARN,
    pretty_kw_name,
)
from robotframework_find_unused.visitors.robot.library_import import LibraryData


class PartialCliReporterCustomKeywordDefinitions(PartialReporter_CustomKeywordDefinitions):
    """
    Partial CLI reporter for discovering custom keyword definitions.
    """

    def on_get_custom_keyword_definitions_start(self, files: list[LibraryDoc]):
        click.echo("Gathering custom keyword definitions...")

    def on_get_custom_keyword_definitions_end(
        self,
        files: list[LibraryDoc],
        keywords: list[KeywordData],
    ):
        if len(keywords) == 0:
            click.echo(f"{ERROR} Found {len(keywords)} custom keyword definitions")
            if self.options.verbose == VERBOSE_NO:
                click.echo(
                    f"{NOTE} Run with `--verbose --verbose` or `-vv` for more details",
                )
            sys.exit(255)
            return

        click.echo(f"{DONE} Found {len(keywords)} custom keyword definitions")

        if self.options.verbose == VERBOSE_NO:
            return

        kw_types: dict[str, list[str]] = {}
        for kw in keywords:
            if kw.type not in kw_types:
                kw_types[kw.type] = []
            kw_types[kw.type].append(pretty_kw_name(kw))

        for kw_type, kw_names in sorted(kw_types.items(), key=lambda x: len(x[1]), reverse=True):
            click.echo(f"{INDENT}{len(kw_names)} keywords of type {kw_type}")

            if self.options.verbose == VERBOSE_SINGLE:
                continue
            for name in kw_names:
                click.echo(f"{INDENT}{INDENT}{name}")


class PartialCliReporterDownloadedKeywordDefinitions(PartialReporter_DownloadedKeywordDefinitions):
    """
    Partial CLI reporter for discovering downloaded keyword definitions.
    """

    def on_get_downloaded_keyword_definitions_start(self, file_paths: list[Path]):
        click.echo("Gathering downloaded library keyword definitions...")

    def on_get_downloaded_keyword_definitions_end(
        self,
        file_paths: list[Path],
        libraries: list[LibraryData],
    ):
        click.echo(
            (WARN if len(libraries) == 0 else DONE)
            + f" Found {len(libraries)} downloaded libraries",
        )

        if self.options.verbose == VERBOSE_NO:
            return

        for lib in libraries:
            if lib.import_error:
                click.echo(f"{INDENT}{lib.name}: {ERROR}")
            elif len(lib.keywords) == 0:
                click.echo(f"{INDENT}{lib.name}: {len(lib.keywords)} keywords {WARN}")
            else:
                click.echo(f"{INDENT}{lib.name}: {len(lib.keywords)} keywords")

    def on_library_parse_error(
        self,
        error: DataError,
        lib_name: str,
    ):
        click.echo(f"{ERROR} Failed to gather keywords from library `{lib_name}`: {error}")
