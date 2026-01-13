import fnmatch
from collections.abc import Callable

import click

from robotframework_find_unused.common.const import NOTE_MARKER, FilterOption, KeywordData


def cli_filter_keywords(  # noqa: PLR0913
    keywords: list[KeywordData],
    *,
    filter_deprecated: FilterOption | None = None,
    filter_private: FilterOption | None = None,
    filter_library: FilterOption | None = None,
    filter_unused: FilterOption | None = None,
    filter_returns: FilterOption | None = None,
    filter_glob: str | None,
) -> list[KeywordData]:
    """
    Filter a list of keywords according to the user options.

    Logs to the user which type of keywords are excluded.

    Returns a filtered list.
    """
    if filter_deprecated:
        keywords = _cli_filter_keywords_by_option(
            keywords,
            filter_deprecated,
            lambda kw: kw.deprecated or False,
            "deprecated",
        )

    if filter_private:
        keywords = _cli_filter_keywords_by_option(
            keywords,
            filter_private,
            lambda kw: kw.private,
            "private",
        )

    if filter_library:
        keywords = _cli_filter_keywords_by_option(
            keywords,
            filter_library,
            lambda kw: kw.type == "LIBRARY",
            "downloaded library",
        )

    if filter_unused:
        keywords = _cli_filter_keywords_by_option(
            keywords,
            filter_unused,
            lambda kw: kw.use_count == 0,
            "unused",
        )

    if filter_returns:
        keywords = _cli_filter_keywords_by_option(
            keywords,
            filter_returns,
            lambda kw: kw.returns is True,
            "returning",
        )

    if filter_glob:
        click.echo(f"Only showing keywords matching '{filter_glob}'")

        pattern = filter_glob.lower()
        keywords = list(
            filter(
                lambda kw: fnmatch.fnmatchcase(kw.name.lower(), pattern),
                keywords,
            ),
        )

    return keywords


def _cli_filter_keywords_by_option(
    keywords: list[KeywordData],
    option: FilterOption,
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
