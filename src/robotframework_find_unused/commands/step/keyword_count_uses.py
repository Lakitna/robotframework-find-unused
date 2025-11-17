from pathlib import Path

import click

from robotframework_find_unused.common.const import (
    DONE_MARKER,
    INDENT,
    VERBOSE_NO,
    WARN_MARKER,
)
from robotframework_find_unused.common.gather_keywords import KeywordData, count_keyword_uses
from robotframework_find_unused.visitors.library_import import LibraryData


def cli_count_keyword_uses(
    file_paths: list[Path],
    keywords: list[KeywordData],
    downloaded_library_keywords: list[LibraryData],
    *,
    verbose: int,
):
    """
    Count keyword uses with RoboCop and keep the user up-to-date on progress
    """
    click.echo("Counting keyword usage...")

    counted_keywords = count_keyword_uses(
        file_paths,
        keywords,
        downloaded_library_keywords,
    )
    _log_keyword_call_stats(counted_keywords, verbose)

    unknown_keywords = [kw for kw in counted_keywords if kw.type == "UNKNOWN"]
    _log_unknown_keyword_stats(unknown_keywords, verbose)

    return counted_keywords


def _log_keyword_call_stats(keywords: list[KeywordData], verbose: int) -> None:
    """
    Output details on calls to the given keywords to the user
    """
    total_uses = sum([kw.use_count for kw in keywords])
    click.echo(
        (WARN_MARKER if total_uses == 0 else DONE_MARKER)
        + f" Processed {total_uses} keyword calls",
    )

    if verbose == VERBOSE_NO:
        return

    kw_type_use_count: dict[str, int] = {}
    for kw in keywords:
        if kw.type not in kw_type_use_count:
            kw_type_use_count[kw.type] = 0
        kw_type_use_count[kw.type] += kw.use_count

    for kw_type, count in sorted(kw_type_use_count.items(), key=lambda x: x[1], reverse=True):
        click.echo(f"{INDENT}{count} calls to keywords of type {kw_type}")

    click.echo(
        (WARN_MARKER if len(keywords) == 0 else DONE_MARKER)
        + f" Found {len(keywords)} unique keywords "
        + click.style("(keyword definitions and calls)", fg="bright_black"),
    )


def _log_unknown_keyword_stats(keywords: list[KeywordData], verbose: int) -> None:
    """
    Output details on keywords for which no definition was found
    """
    if len(keywords) > 0:
        click.echo(
            f"{WARN_MARKER} Found {len(keywords)} called keywords without a definition",
        )

    if verbose == VERBOSE_NO:
        return

    for kw in keywords:
        click.echo(f"{INDENT}{kw.name}")
