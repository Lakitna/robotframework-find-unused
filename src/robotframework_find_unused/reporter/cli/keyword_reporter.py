import sys

import click

from robotframework_find_unused.commands.step.keyword_filter import cli_filter_keywords
from robotframework_find_unused.common.cli import pretty_kw_name
from robotframework_find_unused.common.const import KeywordData
from robotframework_find_unused.common.sort import sort_keywords_by_name
from robotframework_find_unused.reporter.base.keyword_reporter import KeywordReporter

from .partial.count_keywords import PartialCliReporterCountKeywords
from .partial.discover_files import PartialCliReporterDiscoverFiles
from .partial.keyword_definitions import (
    PartialCliReporterCustomKeywordDefinitions,
    PartialCliReporterDownloadedKeywordDefinitions,
)
from .partial.parse_files import PartialCliReporterParseFiles


class KeywordCliReporter(
    KeywordReporter,
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
