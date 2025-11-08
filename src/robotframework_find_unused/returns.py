"""
Implementation of the 'returns' command
"""

import fnmatch
from dataclasses import dataclass

import click
from robocop.config import ConfigManager

from robotframework_find_unused.common.cli import (
    cli_count_keyword_uses,
    cli_filter_keywords_by_option,
    cli_step_gather_files,
    cli_step_get_keyword_definitions,
    pretty_kw_name,
)
from robotframework_find_unused.common.const import KeywordData, KeywordFilterOption


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
    verbose: bool


def cli_returns(file_path: str, options: ReturnOptions):
    """
    Entry point for the CLI command
    """
    robocop_config = ConfigManager(sources=[file_path])

    files = cli_step_gather_files(robocop_config, verbose=options.verbose)
    keywords = cli_step_get_keyword_definitions(files, verbose=options.verbose)
    counted_keywords = cli_count_keyword_uses(
        robocop_config,
        keywords,
        downloaded_library_keywords=[],
        verbose=options.verbose,
    )

    _cli_log_results(counted_keywords, options)


def _cli_log_results(keywords: list[KeywordData], options: ReturnOptions) -> None:
    keywords = cli_filter_keywords_by_option(
        keywords,
        options.deprecated_keywords,
        lambda kw: kw.deprecated or False,
        "deprecated",
    )

    keywords = cli_filter_keywords_by_option(
        keywords,
        options.private_keywords,
        lambda kw: kw.private,
        "private",
    )

    keywords = cli_filter_keywords_by_option(
        keywords,
        options.library_keywords,
        lambda kw: kw.type == "LIBRARY",
        "downloaded library",
    )

    keywords = cli_filter_keywords_by_option(
        keywords,
        options.unused_keywords,
        lambda kw: kw.use_count == 0,
        "unused",
    )

    keywords = cli_filter_keywords_by_option(
        keywords,
        "only",
        lambda kw: kw.returns is True,
        "returning",
    )

    if options.keyword_filter_glob:
        click.echo(f"Only showing keywords matching '{options.keyword_filter_glob}'")

        pattern = options.keyword_filter_glob.lower()
        keywords = list(
            filter(
                lambda kw: fnmatch.fnmatchcase(kw.name.lower(), pattern),
                keywords,
            )
        )

    click.echo()

    if options.show_all_count:
        _cli_log_results_show_count(keywords)
    else:
        _cli_log_results_unused(keywords)


def _cli_log_results_unused(keywords: list[KeywordData]) -> None:
    unused_returns = [kw for kw in keywords if kw.return_use_count == 0]

    click.echo(f"Found {len(unused_returns)} unused keyword returns:")
    for kw in unused_returns:
        click.echo("  " + pretty_kw_name(kw))


def _cli_log_results_show_count(keywords: list[KeywordData]) -> None:
    click.echo("return_use_count\tkeyword_name")

    sorted_keywords = sorted(keywords, key=lambda kw: kw.return_use_count)

    for kw in sorted_keywords:
        click.echo("\t".join([str(kw.return_use_count), pretty_kw_name(kw)]))
