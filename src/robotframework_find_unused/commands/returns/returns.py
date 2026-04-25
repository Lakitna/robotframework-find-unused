"""
Implementation of the 'returns' command
"""

import click

from robotframework_find_unused.commands.step.discover_files import cli_discover_file_paths
from robotframework_find_unused.commands.step.keyword_count_uses import cli_count_keyword_uses
from robotframework_find_unused.commands.step.keyword_definitions import (
    cli_step_get_custom_keyword_definitions,
)
from robotframework_find_unused.commands.step.keyword_filter import cli_filter_keywords
from robotframework_find_unused.commands.step.lib_keyword_definitions import (
    cli_step_get_downloaded_lib_keywords,
)
from robotframework_find_unused.commands.step.parse_files import cli_step_parse_files_with_libdoc
from robotframework_find_unused.common.cli import pretty_kw_name
from robotframework_find_unused.common.const import KeywordData
from robotframework_find_unused.common.sort import sort_keywords_by_name
from robotframework_find_unused.reporter.base.return_reporter import ReturnReporter

from .options import ReturnOptions


def cli_returns(options: ReturnOptions, reporter: ReturnReporter) -> None:
    """
    Entry point for the CLI command
    """
    reporter.on_command_start()

    file_paths = cli_discover_file_paths(options.source_path, reporter=reporter)
    if file_paths is None:
        return

    files = cli_step_parse_files_with_libdoc(file_paths, reporter=reporter)

    keywords = cli_step_get_custom_keyword_definitions(
        files,
        reporter=reporter,
        enrich_py_keywords=True,
    )
    if len(keywords) == 0:
        return

    downloaded_library_keywords = cli_step_get_downloaded_lib_keywords(
        file_paths,
        reporter=reporter,
        enrich_py_keywords=options.library_keywords != "exclude",
    )

    counted_keywords = cli_count_keyword_uses(
        file_paths,
        keywords,
        downloaded_library_keywords,
        reporter=reporter,
    )

    if options.library_keywords != "exclude" and options.unused_keywords != "exclude":
        for lib in downloaded_library_keywords:
            for kw in lib.keywords:
                if kw in counted_keywords:
                    continue
                counted_keywords.append(kw)

    counted_keywords = cli_filter_keywords(
        counted_keywords,
        filter_deprecated=options.deprecated_keywords,
        filter_private=options.private_keywords,
        filter_library=options.library_keywords,
        filter_unused=options.unused_keywords,
        filter_returns="only",
        filter_glob=options.keyword_filter_glob,
    )

    reporter.on_command_end(counted_keywords)


def _cli_log_results(keywords: list[KeywordData], options: ReturnOptions) -> None:
    click.echo()

    if options.show_all_count:
        sorted_keywords = sort_keywords_by_name(keywords)
        sorted_keywords = sorted(sorted_keywords, key=lambda kw: kw.return_use_count)

        click.echo("return_use_count\tkeyword_name")
        for kw in sorted_keywords:
            click.echo("\t".join([str(kw.return_use_count), pretty_kw_name(kw)]))
    else:
        unused_returns = [kw for kw in keywords if kw.return_use_count == 0]
        unused_returns = sort_keywords_by_name(unused_returns)

        click.echo(f"Found {len(unused_returns)} unused keyword returns:")
        for kw in unused_returns:
            click.echo("  " + pretty_kw_name(kw))


def _exit_code(keywords: list[KeywordData]) -> int:
    unused_returns = [kw for kw in keywords if kw.return_use_count == 0]
    exit_code = len(unused_returns)
    return min(exit_code, 200)
