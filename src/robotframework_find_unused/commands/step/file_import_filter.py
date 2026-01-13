import fnmatch
from collections.abc import Callable

import click

from robotframework_find_unused.common.const import NOTE_MARKER, FileUseData, FilterOption


def cli_filter_file_imports(  # noqa: PLR0913
    files: list[FileUseData],
    *,
    filter_library: FilterOption | None = None,
    filter_variable: FilterOption | None = None,
    filter_resource: FilterOption | None = None,
    filter_unused: FilterOption | None = None,
    filter_glob: str | None,
) -> list[FileUseData]:
    """
    Filter a list of file uses according to the user options.

    Logs to the user which type of file uses are excluded.

    Returns a filtered list.
    """
    if filter_library:
        files = _cli_filter_file_imports_by_option(
            files,
            filter_library,
            lambda f: "LIBRARY" in f.type,
            "custom library",
        )

    if filter_variable:
        files = _cli_filter_file_imports_by_option(
            files,
            filter_variable,
            lambda f: "VARIABLE" in f.type,
            "variable",
        )

    if filter_resource:
        files = _cli_filter_file_imports_by_option(
            files,
            filter_resource,
            lambda f: "RESOURCE" in f.type,
            "resource",
        )

    if filter_unused:
        files = _cli_filter_file_imports_by_option(
            files,
            filter_unused,
            lambda f: len(f.used_by) == 0,
            "unused",
        )

    if filter_glob:
        click.echo(f"{NOTE_MARKER} Only showing files matching '{filter_glob}'")

        pattern = filter_glob.lower()
        files = list(
            filter(
                lambda path: fnmatch.fnmatchcase(path.path_absolute.as_posix(), pattern),
                files,
            ),
        )

    return files


def _cli_filter_file_imports_by_option(
    files: list[FileUseData],
    option: FilterOption,
    matcher_fn: Callable[[FileUseData], bool],
    descriptor: str,
) -> list[FileUseData]:
    """
    Filter files on given condition function. Let the user know what was filtered.
    """
    opt = option.lower()

    if opt == "include":
        return files

    if opt == "exclude":
        click.echo(f"{NOTE_MARKER} Excluding {descriptor} file imports")
        return list(filter(lambda kw: matcher_fn(kw) is False, files))

    if opt == "only":
        click.echo(f"{NOTE_MARKER} Only showing {descriptor} file imports")
        return list(filter(lambda kw: matcher_fn(kw) is True, files))

    msg = f"Unexpected value '{option}' when filtering {descriptor} file imports"
    raise TypeError(msg)
