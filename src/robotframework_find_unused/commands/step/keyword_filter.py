import fnmatch
from collections.abc import Callable

from robotframework_find_unused.common.const import FilterOption, KeywordData
from robotframework_find_unused.reporter.base.argument_reporter import ArgumentReporter
from robotframework_find_unused.reporter.base.keyword_reporter import KeywordReporter
from robotframework_find_unused.reporter.base.return_reporter import ReturnReporter


def step_filter_keywords(
    keywords: list[KeywordData],
    *,
    reporter: KeywordReporter | ReturnReporter | ArgumentReporter,
) -> list[KeywordData]:
    """
    Filter a list of keywords according to the user options.

    Logs to the user which type of keywords are excluded.

    Returns a filtered list.
    """
    if reporter.options.deprecated_keywords:
        keywords = _cli_filter_keywords_by_option(
            keywords,
            reporter.options.deprecated_keywords,
            lambda kw: kw.deprecated or False,
            "deprecated",
            reporter=reporter,
        )

    if reporter.options.private_keywords:
        keywords = _cli_filter_keywords_by_option(
            keywords,
            reporter.options.private_keywords,
            lambda kw: kw.private,
            "private",
            reporter=reporter,
        )

    if reporter.options.library_keywords:
        keywords = _cli_filter_keywords_by_option(
            keywords,
            reporter.options.library_keywords,
            lambda kw: kw.type == "LIBRARY",
            "downloaded library",
            reporter=reporter,
        )

    if not isinstance(reporter, KeywordReporter) and reporter.options.unused_keywords:
        keywords = _cli_filter_keywords_by_option(
            keywords,
            reporter.options.unused_keywords,
            lambda kw: kw.use_count == 0,
            "unused",
            reporter=reporter,
        )

    if isinstance(reporter, ReturnReporter):
        keywords = _cli_filter_keywords_by_option(
            keywords,
            "only",
            lambda kw: kw.returns is True,
            "returning",
            reporter=reporter,
        )

    if reporter.options.keyword_filter_glob:
        pattern = reporter.options.keyword_filter_glob.lower()
        filtered_keywords = list(
            filter(
                lambda kw: fnmatch.fnmatchcase(kw.name.lower(), pattern),
                keywords,
            ),
        )

        reporter.on_filter_keywords(
            keywords,
            filtered_keywords,
            f"Only showing keywords matching '{reporter.options.keyword_filter_glob}'",
        )

        keywords = filtered_keywords

    return keywords


def _cli_filter_keywords_by_option(
    keywords: list[KeywordData],
    option: FilterOption,
    matcher_fn: Callable[[KeywordData], bool],
    descriptor: str,
    *,
    reporter: KeywordReporter | ReturnReporter | ArgumentReporter,
) -> list[KeywordData]:
    """
    Filter keywords on given condition function. Let the user know what was filtered.
    """
    opt = option.lower()

    if opt == "include":
        return keywords

    if opt == "exclude":
        filtered_keywords = list(filter(lambda kw: matcher_fn(kw) is False, keywords))
        reporter.on_filter_keywords(
            keywords,
            filtered_keywords,
            f"Excluding {descriptor} keywords",
        )
        return filtered_keywords

    if opt == "only":
        filtered_keywords = list(filter(lambda kw: matcher_fn(kw) is True, keywords))
        reporter.on_filter_keywords(
            keywords,
            filtered_keywords,
            f"Only showing {descriptor} keywords",
        )
        return filtered_keywords

    msg = f"Unexpected value '{option}' when filtering {descriptor} keywords"
    raise TypeError(msg)
