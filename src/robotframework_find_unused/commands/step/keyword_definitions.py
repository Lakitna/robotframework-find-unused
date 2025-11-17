import click
from robot.libdocpkg.model import LibraryDoc

from robotframework_find_unused.common.cli import pretty_kw_name
from robotframework_find_unused.common.const import (
    DONE_MARKER,
    ERROR_MARKER,
    INDENT,
    VERBOSE_NO,
    VERBOSE_SINGLE,
)
from robotframework_find_unused.common.gather_keywords import (
    KeywordData,
    get_custom_keyword_definitions,
)


def cli_step_get_custom_keyword_definitions(files: list[LibraryDoc], *, verbose: int):
    """
    Gather keyword definitions from already processed files and keep the user up-to-date on progress
    """
    click.echo("Gathering custom keyword definitions...")

    keywords = get_custom_keyword_definitions(files)

    _log_keyword_stats(keywords, verbose)
    return keywords


def _log_keyword_stats(keywords: list[KeywordData], verbose: int) -> None:
    """
    Output details on the given keywords to the user
    """
    click.echo(
        (ERROR_MARKER if len(keywords) == 0 else DONE_MARKER)
        + f" Found {len(keywords)} custom keyword definitions",
    )

    if verbose == VERBOSE_NO:
        return

    kw_types: dict[str, list[str]] = {}
    for kw in keywords:
        if kw.type not in kw_types:
            kw_types[kw.type] = []
        kw_types[kw.type].append(pretty_kw_name(kw))

    for kw_type, kw_names in sorted(kw_types.items(), key=lambda x: len(x[1]), reverse=True):
        click.echo(f"{INDENT}{len(kw_names)} keywords of type {kw_type}")

        if verbose == VERBOSE_SINGLE:
            continue
        for name in kw_names:
            click.echo(f"{INDENT}{INDENT}{name}")
