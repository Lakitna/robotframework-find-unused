import fnmatch
from collections.abc import Callable

from robotframework_find_unused.common.const import FileUseData, FilterOption
from robotframework_find_unused.reporter.base.file_reporter import FileReporter


def step_filter_file_imports(
    files: list[FileUseData],
    *,
    reporter: FileReporter,
) -> list[FileUseData]:
    """
    Filter a list of file uses according to the user options.

    Logs to the user which type of file uses are excluded.

    Returns a filtered list.
    """
    if reporter.options.library_files:
        files = _filter_file_imports_by_option(
            files,
            reporter.options.library_files,
            lambda f: "LIBRARY" in f.type,
            "custom library",
            reporter=reporter,
        )

    if reporter.options.variable_files:
        files = _filter_file_imports_by_option(
            files,
            reporter.options.variable_files,
            lambda f: "VARIABLE" in f.type,
            "variable",
            reporter=reporter,
        )

    if reporter.options.resource_files:
        files = _filter_file_imports_by_option(
            files,
            reporter.options.resource_files,
            lambda f: "RESOURCE" in f.type,
            "resource",
            reporter=reporter,
        )

    if reporter.options.unused_files:
        files = _filter_file_imports_by_option(
            files,
            reporter.options.unused_files,
            lambda f: len(f.used_by) == 0,
            "unused",
            reporter=reporter,
        )

    if reporter.options.path_filter_glob:
        pattern = reporter.options.path_filter_glob.lower()
        filtered_files = list(
            filter(
                lambda path: fnmatch.fnmatchcase(path.resolved_to.path.as_posix(), pattern),
                files,
            ),
        )
        reporter.on_filter_files(
            files,
            filtered_files,
            f"Only showing files matching '{reporter.options.path_filter_glob}'",
        )

        files = filtered_files

    return files


def _filter_file_imports_by_option(
    files: list[FileUseData],
    option: FilterOption,
    matcher_fn: Callable[[FileUseData], bool],
    descriptor: str,
    *,
    reporter: FileReporter,
) -> list[FileUseData]:
    """
    Filter files on given condition function. Let the user know what was filtered.
    """
    opt = option.lower()

    if opt == "include":
        return files

    if opt == "exclude":
        filtered_files = list(filter(lambda kw: matcher_fn(kw) is False, files))
        reporter.on_filter_files(
            files,
            filtered_files,
            f"Excluding {descriptor} file imports",
        )
        return filtered_files

    if opt == "only":
        filtered_files = list(filter(lambda kw: matcher_fn(kw) is True, files))
        reporter.on_filter_files(
            files,
            filtered_files,
            f"Only showing {descriptor} file imports",
        )
        return filtered_files

    msg = f"Unexpected value '{option}' when filtering {descriptor} file imports"
    raise TypeError(msg)
