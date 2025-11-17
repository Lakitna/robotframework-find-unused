import sys
from collections.abc import Callable

import click

from robotframework_find_unused.common.const import NOTE_MARKER, VERBOSE_DOUBLE, KeywordFilterOption
from robotframework_find_unused.common.gather_keywords import KeywordData


def pretty_kw_name(keyword: KeywordData) -> str:
    """
    Format keyword name for output to the user
    """
    name = keyword.name

    if keyword.library:
        name = click.style(keyword.library + ".", fg="bright_black") + name

    if keyword.deprecated is True:
        name += " " + click.style("[DEPRECATED]", fg="red")

    return name


def cli_filter_keywords_by_option(
    keywords: list[KeywordData],
    option: KeywordFilterOption,
    matcher_fn: Callable[[KeywordData], bool],
    descriptor: str,
) -> list[KeywordData]:
    """
    Filter keywords on given condition function. Let the user know what was filtered.
    """
    opt = option.lower()

    if opt == "include":
        return keywords

    if opt == "exclude":
        click.echo(f"{NOTE_MARKER} Excluding {descriptor} keywords")
        return list(filter(lambda kw: matcher_fn(kw) is False, keywords))

    if opt == "only":
        click.echo(f"{NOTE_MARKER} Only showing {descriptor} keywords")
        return list(filter(lambda kw: matcher_fn(kw) is True, keywords))

    msg = f"Unexpected value '{option}' when filtering {descriptor} keywords"
    raise TypeError(msg)


def cli_hard_exit(verbose: int) -> None:
    """
    Immediately hard exit app. Use when something went wrong.
    """
    if verbose < VERBOSE_DOUBLE:
        click.echo(f"{NOTE_MARKER} Run with `--verbose --verbose` or `-vv` for more details")
    sys.exit(255)
    return 255
