"""
Implementation of the 'keywords' command
"""

import fnmatch
from dataclasses import dataclass

import click
from robocop import Config

from robotframework_find_unused.common.cli import (
    cli_count_keyword_uses,
    cli_filter_keywords_by_option,
    cli_step_gather_files,
    cli_step_get_downloaded_lib_keywords,
    cli_step_get_keyword_definitions,
    pretty_kw_name,
)
from robotframework_find_unused.common.const import KeywordData, KeywordFilterOption


@dataclass
class KeywordOptions:
    """
    Command line options for the 'keywords' command
    """

    show_all_count: bool
    deprecated_keywords: KeywordFilterOption
    private_keywords: KeywordFilterOption
    library_keywords: KeywordFilterOption
    keyword_filter_glob: str | None
    verbose: bool


def cli_keywords(file_path: str, options: KeywordOptions):
    """
    Entry point for the CLI command
    """
    robocop_config = Config()
    robocop_config.paths = [file_path]

    files = cli_step_gather_files(robocop_config, verbose=options.verbose)
    keywords = cli_step_get_keyword_definitions(files, verbose=options.verbose)
    downloaded_library_keywords = cli_step_get_downloaded_lib_keywords(
        robocop_config,
        verbose=options.verbose,
    )
    counted_keywords = cli_count_keyword_uses(
        robocop_config,
        keywords,
        downloaded_library_keywords,
        verbose=options.verbose,
    )

    _cli_log_results(counted_keywords, options)


def _cli_log_results(keywords: list[KeywordData], options: KeywordOptions) -> None:
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
        sorted_keywords = sorted(keywords, key=lambda kw: kw.use_count)

        click.echo("use_count\tkeyword_name")
        for kw in sorted_keywords:
            click.echo("\t".join([str(kw.use_count), pretty_kw_name(kw)]))
    else:
        unused_keywords = [kw for kw in keywords if kw.use_count == 0]

        click.echo(f"Found {len(unused_keywords)} unused keywords:")
        for kw in unused_keywords:
            click.echo("  " + pretty_kw_name(kw))
