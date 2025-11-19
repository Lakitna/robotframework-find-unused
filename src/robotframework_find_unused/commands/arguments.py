"""
Implementation of the 'arguments' command
"""

from dataclasses import dataclass

import click

from robotframework_find_unused.commands.step.discover_files import cli_discover_file_paths
from robotframework_find_unused.common.cli import cli_hard_exit, pretty_kw_name
from robotframework_find_unused.common.const import INDENT, KeywordData, KeywordFilterOption
from robotframework_find_unused.common.sort import sort_keywords_by_name

from .step.keyword_count_uses import cli_count_keyword_uses
from .step.keyword_definitions import cli_step_get_custom_keyword_definitions
from .step.keyword_filter import cli_filter_keywords
from .step.lib_keyword_definitions import cli_step_get_downloaded_lib_keywords
from .step.parse_files import cli_step_parse_files


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
    verbose: int
    source_path: str


def cli_arguments(options: ArgumentsOptions):
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
        filter_glob=options.keyword_filter_glob,
    )
    _cli_log_results(counted_keywords, options)
    return _exit_code(counted_keywords)


def _cli_log_results(keywords: list[KeywordData], options: ArgumentsOptions) -> None:
    click.echo()

    keywords = sort_keywords_by_name(keywords)

    for kw in keywords:
        if kw.argument_use_count is None:
            continue

        if options.show_all_count:
            _cli_log_results_show_count(kw)
        else:
            _cli_log_results_unused(kw)


def _cli_log_results_unused(kw: KeywordData) -> None:
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


def _cli_log_results_show_count(kw: KeywordData) -> None:
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


def _exit_code(keywords: list[KeywordData]) -> int:
    unused_args = 0
    for kw in keywords:
        if not kw.argument_use_count:
            continue

        for count in kw.argument_use_count.values():
            if count == 0:
                unused_args += 1

    exit_code = unused_args
    return min(exit_code, 200)
