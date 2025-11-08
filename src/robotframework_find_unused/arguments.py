"""
Implementation of the 'arguments' command
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
from robotframework_find_unused.common.const import INDENT, KeywordData, KeywordFilterOption


@dataclass
class ArgumentsOptions:
    """
    Command line options for the 'arguments' command
    """

    deprecated_keywords: KeywordFilterOption
    private_keywords: KeywordFilterOption
    library_keywords: KeywordFilterOption
    unused_keywords: KeywordFilterOption
    keyword_filter_glob: str | None
    show_all_count: bool
    verbose: bool


def cli_arguments(file_path: str, options: ArgumentsOptions):
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


def _cli_log_results(keywords: list[KeywordData], options: ArgumentsOptions) -> None:
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

    for kw in keywords:
        if kw.argument_use_count is None:
            continue

        if options.show_all_count:
            cli_log_results_show_count(kw)
        else:
            cli_log_results_unused(kw)


def cli_log_results_unused(kw: KeywordData):
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


def cli_log_results_show_count(kw: KeywordData):
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
