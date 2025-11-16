"""
Implementation of the 'returns' command
"""

import fnmatch
from dataclasses import dataclass

import click

from robotframework_find_unused.commands.step.discover_files import cli_discover_file_paths
from robotframework_find_unused.common.cli import (
    cli_filter_keywords_by_option,
    cli_hard_exit,
    pretty_kw_name,
)
from robotframework_find_unused.common.const import KeywordData, KeywordFilterOption

from .step.keyword_count_uses import cli_count_keyword_uses
from .step.keyword_definitions import cli_step_get_custom_keyword_definitions
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

    _cli_log_results(counted_keywords, options)
    return 0


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
            ),
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
