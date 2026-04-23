import sys
from pathlib import Path

import click
from robot.libdocpkg.model import LibraryDoc

from robotframework_find_unused.commands.step.keyword_filter import cli_filter_keywords
from robotframework_find_unused.common.cli import pretty_kw_name
from robotframework_find_unused.common.const import (
    DONE_MARKER,
    ERROR_MARKER,
    INDENT,
    NOTE_MARKER,
    VERBOSE_NO,
    VERBOSE_SINGLE,
    WARN_MARKER,
    KeywordData,
)
from robotframework_find_unused.common.sort import sort_keywords_by_name
from robotframework_find_unused.reporter.base.keyword_reporter import KeywordReporter
from robotframework_find_unused.visitors.robot.library_import import LibraryData

from .partial.discover_files import PartialCliReporterDiscoverFiles


class KeywordCliReporter(KeywordReporter, PartialCliReporterDiscoverFiles):
    """
    CLI reporter for keyword command.
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
                f"{WARN_MARKER} Failed to parse {len(parse_errors)} files. Files will be ignored",
            )
            for error in parse_errors:
                click.echo(f"{INDENT}{WARN_MARKER} {error}")

        click.echo(f"{DONE_MARKER} Parsed {len(files)} files")

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

    def on_get_custom_keyword_definitions_start(self, files: list[LibraryDoc]):
        click.echo("Gathering custom keyword definitions...")

    def on_get_custom_keyword_definitions_end(
        self,
        files: list[LibraryDoc],
        keywords: list[KeywordData],
    ):
        if len(keywords) == 0:
            click.echo(f"{ERROR_MARKER} Found {len(keywords)} custom keyword definitions")
            if self.options.verbose == VERBOSE_NO:
                click.echo(
                    f"{NOTE_MARKER} Run with `--verbose --verbose` or `-vv` for more details",
                )
            sys.exit(255)
            return

        click.echo(f"{DONE_MARKER} Found {len(keywords)} custom keyword definitions")

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

    def on_get_downloaded_keyword_definitions_start(self, file_paths: list[Path]):
        click.echo("Gathering downloaded library keyword definitions...")

    def on_get_downloaded_keyword_definitions_end(
        self,
        file_paths: list[Path],
        libraries: list[LibraryData],
    ):
        click.echo(
            (WARN_MARKER if len(libraries) == 0 else DONE_MARKER)
            + f" Found {len(libraries)} downloaded libraries",
        )

        if self.options.verbose == VERBOSE_NO:
            return

        for lib in libraries:
            if len(lib.keywords) == 0:
                # Import error
                click.echo(f"{INDENT}{lib.name}: {ERROR_MARKER}")
            else:
                click.echo(f"{INDENT}{lib.name}: {len(lib.keywords)} keywords")

    def on_count_keyword_uses_start(
        self,
        file_paths: list[Path],
        keywords: list[KeywordData],
        downloaded_libraries: list[LibraryData],
    ):
        click.echo("Counting keyword usage...")

    def on_count_keyword_uses_end(
        self,
        file_paths: list[Path],
        keywords: list[KeywordData],
        downloaded_libraries: list[LibraryData],
        counted_keywords: list[KeywordData],
    ):
        total_uses = sum([kw.use_count for kw in counted_keywords])
        click.echo(
            (WARN_MARKER if total_uses == 0 else DONE_MARKER)
            + f" Processed {total_uses} keyword calls",
        )

        if self.options.verbose > VERBOSE_NO:
            kw_type_use_count: dict[str, int] = {}
            for kw in counted_keywords:
                if kw.type not in kw_type_use_count:
                    kw_type_use_count[kw.type] = 0
                kw_type_use_count[kw.type] += kw.use_count

            for kw_type, count in sorted(
                kw_type_use_count.items(),
                key=lambda x: x[1],
                reverse=True,
            ):
                click.echo(f"{INDENT}{count} calls to keywords of type {kw_type}")

            click.echo(
                (WARN_MARKER if len(counted_keywords) == 0 else DONE_MARKER)
                + f" Found {len(counted_keywords)} unique keywords "
                + click.style("(keyword definitions and calls)", fg="bright_black"),
            )

        unknown_keywords = [kw for kw in counted_keywords if kw.type == "UNKNOWN"]
        if len(unknown_keywords) > 0:
            click.echo(
                f"{WARN_MARKER} Found {len(unknown_keywords)} called keywords without a definition",
            )

        if self.options.verbose > VERBOSE_NO:
            for kw in unknown_keywords:
                click.echo(f"{INDENT}{kw.name}")

    def on_command_end(self, counted_keywords: list[KeywordData]):
        counted_keywords = cli_filter_keywords(
            counted_keywords,
            filter_deprecated=self.options.deprecated_keywords,
            filter_private=self.options.private_keywords,
            filter_library=self.options.library_keywords,
            filter_glob=self.options.keyword_filter_glob,
        )

        click.echo()

        if self.options.show_all_count:
            sorted_keywords = sort_keywords_by_name(counted_keywords)
            sorted_keywords = sorted(sorted_keywords, key=lambda kw: kw.use_count)

            click.echo("use_count\tkeyword_name")
            for kw in sorted_keywords:
                click.echo("\t".join([str(kw.use_count), pretty_kw_name(kw)]))
        else:
            unused_keywords = [kw for kw in counted_keywords if kw.use_count == 0]
            unused_keywords = sort_keywords_by_name(unused_keywords)

            click.echo(f"Found {len(unused_keywords)} unused keywords:")
            for kw in unused_keywords:
                click.echo("  " + pretty_kw_name(kw))

        unused_keywords = [kw for kw in counted_keywords if kw.use_count == 0]
        exit_code = len(unused_keywords)
        sys.exit(min(exit_code, 200))
