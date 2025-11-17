"""
Implementation of the 'returns' command
"""

from dataclasses import dataclass

import click

from robotframework_find_unused.commands.step.discover_files import cli_discover_file_paths
from robotframework_find_unused.common.cli import cli_hard_exit, pretty_kw_name
from robotframework_find_unused.common.const import KeywordData, KeywordFilterOption

from .step.keyword_count_uses import cli_count_keyword_uses
from .step.keyword_definitions import cli_step_get_custom_keyword_definitions
from .step.keyword_filter import cli_filter_keywords
from .step.lib_keyword_definitions import cli_step_get_downloaded_lib_keywords
from .step.parse_files import cli_step_parse_files


@dataclass
class ReturnOptions:
    """
    Command line options for the 'returns' command
    """

    show_all_count: bool
    deprecated_keywords: KeywordFilterOption
    private_keywords: KeywordFilterOption
    library_keywords: KeywordFilterOption
    unused_keywords: KeywordFilterOption
    keyword_filter_glob: str | None
    verbose: int
    source_path: str


def cli_returns(options: ReturnOptions):
    """
    Entry point for the CLI command
    """
    file_paths = cli_discover_file_paths(options.source_path, verbose=options.verbose)
    if len(file_paths) == 0:
        return cli_hard_exit(options.verbose)

    files = cli_step_parse_files(
        file_paths,
        verbose=options.verbose,
    )

    keywords = cli_step_get_custom_keyword_definitions(
        files,
        verbose=options.verbose,
    )
    if len(keywords) == 0:
        return cli_hard_exit(options.verbose)

    downloaded_library_keywords = cli_step_get_downloaded_lib_keywords(
        file_paths,
        verbose=options.verbose,
    )

    counted_keywords = cli_count_keyword_uses(
        file_paths,
        keywords,
        downloaded_library_keywords=downloaded_library_keywords,
        verbose=options.verbose,
    )

    counted_keywords = cli_filter_keywords(
        counted_keywords,
        filter_deprecated=options.deprecated_keywords,
        filter_private=options.private_keywords,
        filter_library=options.library_keywords,
        filter_unused=options.unused_keywords,
        filter_returns="only",
        filter_glob=options.keyword_filter_glob,
    )
    _cli_log_results(counted_keywords, options)
    return _exit_code(counted_keywords)


def _cli_log_results(keywords: list[KeywordData], options: ReturnOptions) -> None:
    click.echo()

    if options.show_all_count:
        click.echo("return_use_count\tkeyword_name")

        sorted_keywords = sorted(keywords, key=lambda kw: kw.return_use_count)

        for kw in sorted_keywords:
            click.echo("\t".join([str(kw.return_use_count), pretty_kw_name(kw)]))
    else:
        unused_returns = [kw for kw in keywords if kw.return_use_count == 0]

        click.echo(f"Found {len(unused_returns)} unused keyword returns:")
        for kw in unused_returns:
            click.echo("  " + pretty_kw_name(kw))


def _exit_code(keywords: list[KeywordData]) -> int:
    unused_returns = [kw for kw in keywords if kw.return_use_count == 0]
    exit_code = len(unused_returns)
    return min(exit_code, 200)
