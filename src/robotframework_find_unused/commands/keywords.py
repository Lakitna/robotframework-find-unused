"""
Implementation of the 'keywords' command
"""

from dataclasses import dataclass

import click

from robotframework_find_unused.common.cli import cli_hard_exit, pretty_kw_name
from robotframework_find_unused.common.const import FilterOption, KeywordData
from robotframework_find_unused.common.sort import sort_keywords_by_name

from .step.discover_files import cli_discover_file_paths
from .step.keyword_count_uses import cli_count_keyword_uses
from .step.keyword_definitions import cli_step_get_custom_keyword_definitions
from .step.keyword_filter import cli_filter_keywords
from .step.lib_keyword_definitions import cli_step_get_downloaded_lib_keywords
from .step.parse_files import cli_step_parse_files_with_libdoc


@dataclass
class KeywordOptions:
    """
    Command line options for the 'keywords' command
    """

    show_all_count: bool
    deprecated_keywords: FilterOption
    private_keywords: FilterOption
    library_keywords: FilterOption
    unused_library_keywords: FilterOption
    keyword_filter_glob: str | None
    verbose: int
    source_path: str


def cli_keywords(options: KeywordOptions) -> int:
    """
    Entry point for the CLI command
    """
    file_paths = cli_discover_file_paths(options.source_path, verbose=options.verbose)
    if len(file_paths) == 0:
        return cli_hard_exit(options.verbose)

    files = cli_step_parse_files_with_libdoc(
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

    if options.library_keywords != "exclude" and options.unused_library_keywords != "exclude":
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
        filter_glob=options.keyword_filter_glob,
    )
    _cli_log_results(counted_keywords, options)
    return _exit_code(counted_keywords)


def _cli_log_results(keywords: list[KeywordData], options: KeywordOptions) -> None:
    click.echo()

    if options.show_all_count:
        sorted_keywords = sort_keywords_by_name(keywords)
        sorted_keywords = sorted(sorted_keywords, key=lambda kw: kw.use_count)

        click.echo("use_count\tkeyword_name")
        for kw in sorted_keywords:
            click.echo("\t".join([str(kw.use_count), pretty_kw_name(kw)]))
    else:
        unused_keywords = [kw for kw in keywords if kw.use_count == 0]
        unused_keywords = sort_keywords_by_name(unused_keywords)

        click.echo(f"Found {len(unused_keywords)} unused keywords:")
        for kw in unused_keywords:
            click.echo("  " + pretty_kw_name(kw))


def _exit_code(keywords: list[KeywordData]) -> int:
    unused_keywords = [kw for kw in keywords if kw.use_count == 0]
    exit_code = len(unused_keywords)
    return min(exit_code, 200)
