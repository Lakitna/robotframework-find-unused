from typing import cast

import click
from robot.libdocpkg.model import KeywordDoc, LibraryDoc

from robotframework_find_unused.common.cli import pretty_kw_name
from robotframework_find_unused.common.const import (
    DONE_MARKER,
    ERROR_MARKER,
    INDENT,
    VERBOSE_NO,
    VERBOSE_SINGLE,
    KeywordData,
)
from robotframework_find_unused.common.convert import libdoc_keyword_to_keyword_data
from robotframework_find_unused.common.enrich_python_keywords import enrich_python_keyword_data


def cli_step_get_custom_keyword_definitions(
    files: list[LibraryDoc],
    *,
    verbose: int,
    enrich_py_keywords: bool = False,
):
    """
    Gather keyword definitions in the given scope with LibDoc and show progress
    """
    click.echo("Gathering custom keyword definitions...")

    keywords = _get_custom_keyword_definitions(
        files,
        enrich_py_keywords=enrich_py_keywords,
    )

    _log_keyword_stats(keywords, verbose)
    return keywords


def _get_custom_keyword_definitions(
    files: list[LibraryDoc],
    *,
    enrich_py_keywords: bool = False,
) -> list[KeywordData]:
    """
    Gather keyword definitions in the given scope with LibDoc

    Libdoc supports .robot, .resource, .py, and downloaded libs
    """
    keywords: list[KeywordData] = []
    for file in files:
        if file.type == "SUITE":
            file_type = "CUSTOM_SUITE"
        elif file.type == "LIBRARY":
            file_type = "CUSTOM_LIBRARY"
        elif file.type == "RESOURCE":
            file_type = "CUSTOM_RESOURCE"
        else:
            raise ValueError("Unexpected file type " + file.type)

        if file_type == "CUSTOM_LIBRARY" and enrich_py_keywords:
            enriched_keywords = enrich_python_keyword_data(file)
            for keyword in enriched_keywords:
                keywords.append(
                    libdoc_keyword_to_keyword_data(
                        keyword.doc,
                        file_type,
                        keyword.returns,
                    ),
                )
        else:
            # LibDoc provides all the data we need
            for keyword in cast(list[KeywordDoc], file.keywords):
                keywords.append(
                    libdoc_keyword_to_keyword_data(
                        keyword,
                        file_type,
                        # We don't care or will gather this later
                        keyword_returns=None,
                    ),
                )

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
