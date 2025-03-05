from collections.abc import Callable

import click
from robocop import Config
from robot.libdocpkg.model import LibraryDoc

from robotframework_find_unused.common.const import DONE_MARKER, INDENT, KeywordFilterOption
from robotframework_find_unused.common.gather_files import find_files_with_libdoc
from robotframework_find_unused.common.gather_keywords import (
    KeywordData,
    count_keyword_uses,
    get_keyword_definitions_from_files,
)
from robotframework_find_unused.common.gather_variables import count_variable_uses
from robotframework_find_unused.common.robocop_visit import visit_files_with_robocop
from robotframework_find_unused.visitors.library_import import LibraryData, LibraryImportVisitor


def cli_step_gather_files(robocop_config: Config, *, verbose: bool):
    """
    Gather files with libdoc and keep the user up-to-date on progress
    """
    click.echo("Gathering files with LibDoc...")

    robocop_config.filetypes = [".robot", ".resource", ".py"]
    files = find_files_with_libdoc(robocop_config)

    click.echo(f"{DONE_MARKER} Found and processed {len(files)} files")

    if verbose:
        log_file_stats(files)
    return files


def cli_step_get_keyword_definitions(files: list[LibraryDoc], *, verbose: bool):
    """
    Gather keyword definitions from already processed files and keep the user up-to-date on progress
    """
    click.echo("Gathering keyword definitions from files...")

    keywords = get_keyword_definitions_from_files(files)
    click.echo(f"{DONE_MARKER} Found {len(keywords)} keyword definitions")

    if verbose:
        log_keyword_stats(keywords)
    return keywords


def cli_step_get_downloaded_lib_keywords(robocop_config: Config, *, verbose: bool):
    """
    Gather keyword definitions from imported downloaded libraries and show progress

    Will only resolve libraries that are actually imported in an in-scope .robot or .resource file.
    """
    click.echo("Gathering downloaded library keyword names...")

    robocop_config.filetypes = [".robot", ".resource"]
    visitor = LibraryImportVisitor()
    visit_files_with_robocop(robocop_config, visitor)
    downloaded_library = list(visitor.downloaded_libraries.values())

    click.echo(f"{DONE_MARKER} Found {len(downloaded_library)} downloaded libraries")
    if verbose:
        for lib in downloaded_library:
            click.echo(f"{INDENT}{lib.name}: {len(lib.keywords)} keywords")

    return downloaded_library


def cli_count_keyword_uses(
    robocop_config: Config,
    keywords: list[KeywordData],
    downloaded_library_keywords: list[LibraryData],
    *,
    verbose: bool,
):
    """
    Count keyword uses with RoboCop and keep the user up-to-date on progress
    """
    click.echo("Counting keyword usage with RoboCop...")

    counted_keywords = count_keyword_uses(
        robocop_config,
        keywords,
        downloaded_library_keywords,
    )

    click.echo(f"{DONE_MARKER} Found {len(counted_keywords)} unique keywords")
    if verbose:
        log_keyword_stats(counted_keywords)

    total_uses = 0
    for kw in counted_keywords:
        total_uses += kw.use_count
    click.echo(f"{DONE_MARKER} Processed {total_uses} keyword calls")
    if verbose:
        log_keyword_call_stats(counted_keywords)

    return counted_keywords


def cli_count_variable_uses(
    robocop_config: Config,
    *,
    verbose: bool,
):
    """
    Gather variable definitions and count variable uses with RoboCop and show progress
    """
    click.echo("Gathering variables usage with RoboCop...")
    variables = count_variable_uses(robocop_config)
    click.echo(
        f"{DONE_MARKER} Found {len(variables)} unique variables defined in a variables section",
    )
    if verbose:
        unused_variables = [var.name for var in variables if var.use_count == 0]

        try:
            percentage = round(len(unused_variables) / len(variables) * 100, 1)
        except ZeroDivisionError:
            percentage = 0

        click.echo(
            f"{INDENT}{len(unused_variables)} unused variables ({percentage}%)",
        )

        total_uses = 0
        for var in variables:
            total_uses += var.use_count
        click.echo("Variables section variables usage metrics:")
        click.echo(f"{INDENT}Total\t{total_uses} times")

        try:
            average = round(total_uses / len(variables), 1)
        except ZeroDivisionError:
            average = 0
        click.echo(f"{INDENT}Average\t{average} times per variable")

    return variables


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


def log_keyword_stats(keywords: list[KeywordData]):
    """
    Output details on the given keywords to the user
    """
    kw_type_count = {}
    for kw in keywords:
        if kw.type not in kw_type_count:
            kw_type_count[kw.type] = 0
        kw_type_count[kw.type] += 1

    for kw_type in sorted(kw_type_count, key=kw_type_count.get, reverse=True):
        click.echo(f"{INDENT}{kw_type_count[kw_type]} keyword definitions of type {kw_type}")


def log_keyword_call_stats(keywords: list[KeywordData]):
    """
    Output details on calls to the given keywords to the user
    """
    type_call_count = {}
    for kw in keywords:
        if kw.type not in type_call_count:
            type_call_count[kw.type] = 0
        type_call_count[kw.type] += kw.use_count

    for kw_type in sorted(type_call_count, key=type_call_count.get, reverse=True):
        click.echo(
            f"{INDENT}{type_call_count[kw_type]} keyword calls of keyword type {kw_type}",
        )


def log_file_stats(files: list[LibraryDoc]):
    """
    Output details on given files to the user
    """
    file_type_count = {}
    for file in files:
        if file.type not in file_type_count:
            file_type_count[file.type] = 0
        file_type_count[file.type] += 1

    for file_type in sorted(file_type_count, key=file_type_count.get, reverse=True):
        click.echo(f"{INDENT}{file_type_count[file_type]} files of type {file_type}")


def cli_filter_keywords_by_option(
    keywords: list[KeywordData],
    option: KeywordFilterOption,
    matcher_fn: Callable[[KeywordData], bool],
    descriptor: str,
) -> list[KeywordData]:
    """
    Filter keywords on given condition function. Let the user know what was filtered.
    """
    option = option.lower()

    if option == "include":
        return keywords

    if option == "exclude":
        click.echo(f"Excluding {descriptor} keywords")
        return filter(lambda kw: matcher_fn(kw) is False, keywords)

    if option == "only":
        click.echo(f"Only showing {descriptor} keywords")
        return filter(lambda kw: matcher_fn(kw) is True, keywords)

    msg = f"Unexpected value '{option}' when filtering {descriptor} keywords"
    raise TypeError(msg)
