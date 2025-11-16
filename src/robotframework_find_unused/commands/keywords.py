"""
Implementation of the 'keywords' command
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
from robotframework_find_unused.common.const import NOTE_MARKER, KeywordData, KeywordFilterOption

from .step.keyword_count_uses import cli_count_keyword_uses
from .step.keyword_definitions import cli_step_get_custom_keyword_definitions
from .step.lib_keyword_definitions import cli_step_get_downloaded_lib_keywords
from .step.parse_files import cli_step_parse_files


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
    verbose: int
    source_path: str


def cli_keywords(options: KeywordOptions):
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
    if len(keywords) == 0 and options.library_keywords == "exclude":
        return cli_hard_exit(options.verbose)

    downloaded_library_keywords = cli_step_get_downloaded_lib_keywords(
        file_paths,
        verbose=options.verbose,
    )

    counted_keywords = cli_count_keyword_uses(
        file_paths,
        keywords,
        downloaded_library_keywords,
        verbose=options.verbose,
    )

    counted_keywords = _cli_filter_results(counted_keywords, options)
    _cli_log_results(counted_keywords, options)
    return 0


def _cli_filter_results(keywords: list[KeywordData], options: KeywordOptions) -> list[KeywordData]:
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
        click.echo(f"{NOTE_MARKER} Only showing keywords matching '{options.keyword_filter_glob}'")

        pattern = options.keyword_filter_glob.lower()
        keywords = list(
            filter(
                lambda kw: fnmatch.fnmatchcase(kw.name.lower(), pattern),
                keywords,
            ),
        )

    return keywords


def _cli_log_results(keywords: list[KeywordData], options: KeywordOptions) -> None:
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
