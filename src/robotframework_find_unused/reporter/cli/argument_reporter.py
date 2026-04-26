import sys

import click

from robotframework_find_unused.common.cli import pretty_kw_name
from robotframework_find_unused.common.const import INDENT, KeywordData
from robotframework_find_unused.common.sort import sort_keywords_by_name
from robotframework_find_unused.reporter.base.argument_reporter import ArgumentReporter

from .partial.count_keywords import PartialCliReporterCountKeywords
from .partial.discover_files import PartialCliReporterDiscoverFiles
from .partial.keyword_definitions import (
    PartialCliReporterCustomKeywordDefinitions,
    PartialCliReporterDownloadedKeywordDefinitions,
)
from .partial.parse_files import PartialCliReporterParseFiles


class ArgumentCliReporter(
    ArgumentReporter,
    PartialCliReporterDiscoverFiles,
    PartialCliReporterParseFiles,
    PartialCliReporterCountKeywords,
    PartialCliReporterCustomKeywordDefinitions,
    PartialCliReporterDownloadedKeywordDefinitions,
):
    """
    CLI reporter for keyword command.
    """

    def on_command_end(self, counted_keywords: list[KeywordData]):
        click.echo()

        keywords = sort_keywords_by_name(counted_keywords)

        for kw in keywords:
            if kw.argument_use_count is None:
                continue

            if self.options.show_all_count:
                self._log_results_show_count(kw)
            else:
                self._log_results_unused(kw)

        unused_args = 0
        for kw in keywords:
            if not kw.argument_use_count:
                continue

            for count in kw.argument_use_count.values():
                if count == 0:
                    unused_args += 1

        exit_code = unused_args
        sys.exit(min(exit_code, 200))

    def _log_results_unused(self, kw: KeywordData) -> None:
        """
        Output a keywords arguments if they're unused
        """
        if not kw.arguments or len(kw.arguments.argument_names) == 0 or not kw.argument_use_count:
            return

        unused_args = {}
        for arg, count in kw.argument_use_count.items():
            if count == 0:
                unused_args[arg] = 0

        if not unused_args:
            return

        click.echo(pretty_kw_name(kw))

        click.echo(
            f"{INDENT}Unchanged arguments: {len(unused_args)} of {len(kw.argument_use_count)}",
        )
        for arg in unused_args:
            if arg in kw.arguments.defaults:
                click.echo(f"{INDENT}{INDENT}{arg}={kw.arguments.defaults[arg]}")
            else:
                click.echo(f"{INDENT}{INDENT}{arg}")

        click.echo()

    def _log_results_show_count(self, kw: KeywordData) -> None:
        """
        Output a keyword and all it's argument counts
        """
        arguments = kw.argument_use_count

        click.echo(pretty_kw_name(kw))

        if not arguments or len(arguments) == 0:
            click.echo(INDENT + click.style("Keyword has 0 arguments", fg="bright_black"))
            click.echo()
            return

        click.echo(f"{INDENT}use_count\targument")

        for arg, use_count in arguments.items():
            kw_args = kw.arguments
            if kw_args is not None and arg in kw_args.defaults:
                click.echo(f"{INDENT}{use_count}\t\t{arg}={kw_args.defaults[arg]}")
            else:
                click.echo(f"{INDENT}{use_count}\t\t{arg}")

        click.echo()
