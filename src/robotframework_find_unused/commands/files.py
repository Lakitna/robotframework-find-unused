"""
Implementation of the 'files' command
"""

import fnmatch
import sys
from dataclasses import dataclass
from pathlib import Path

import click
from robot.conf import RobotSettings

from robotframework_find_unused.common.cli import cli_hard_exit, pretty_file_path
from robotframework_find_unused.common.const import NOTE_MARKER, FileUseData, FilterOption
from robotframework_find_unused.common.normalize import normalize_file_path
from robotframework_find_unused.convert.convert_path import to_relative_path

from .step.discover_files import cli_discover_file_paths
from .step.file_import_filter import cli_filter_file_imports
from .step.file_import_tree import FileImportTreeBuilder
from .step.parse_file_use import cli_step_parse_file_use


@dataclass
class FileOptions:
    """
    Command line options for the 'files' command
    """

    show_all_count: bool
    library_files: FilterOption
    variable_files: FilterOption
    resource_files: FilterOption
    unused_files: FilterOption
    path_filter_glob: str | None
    show_tree: bool
    tree_max_depth: int
    tree_max_height: int
    verbose: int
    source_path: str
    pythonpath: list[str]


def cli_files(options: FileOptions):
    """
    Entry point for the CLI command
    """
    settings = RobotSettings({"pythonpath": options.pythonpath})
    if settings.pythonpath:
        sys.path = settings.pythonpath + sys.path

    print(sys.path)

    file_paths = cli_discover_file_paths(options.source_path, verbose=options.verbose)
    if len(file_paths) == 0:
        return cli_hard_exit(options.verbose)

    files = cli_step_parse_file_use(
        file_paths,
        Path(options.source_path),
        verbose=options.verbose,
    )

    if options.show_tree:
        _cli_print_grouped_file_trees(files, options)
    _cli_log_results(files, options)

    return _exit_code(files)


def _cli_log_results(files: list[FileUseData], options: FileOptions) -> None:
    click.echo()

    files = [f for f in files if "SUITE" not in f.type]
    files = cli_filter_file_imports(
        files,
        filter_library=options.library_files,
        filter_variable=options.variable_files,
        filter_resource=options.resource_files,
        filter_unused=options.unused_files,
        filter_glob=options.path_filter_glob,
    )

    cwd = Path.cwd().joinpath(options.source_path)
    if options.show_all_count:
        sorted_files = sorted(files, key=lambda f: f.id)
        sorted_files = sorted(sorted_files, key=lambda f: len(f.used_by))

        click.echo("import_count\tfile")
        for file in sorted_files:
            file_path = pretty_file_path(
                to_relative_path(cwd, file.path_absolute),
                file.type,
            )
            click.echo(
                "\t".join(
                    [str(len(file.used_by)), file_path],
                ),
            )
    else:
        sorted_files = sorted(files, key=lambda f: f.id)
        unused_files = [f for f in sorted_files if len(f.used_by) == 0]

        if len(unused_files) == 0:
            click.echo("Found no unused files")
            return

        click.echo(f"Found {len(unused_files)} unused files:")
        for file in unused_files:
            file_path = pretty_file_path(
                to_relative_path(cwd, file.path_absolute),
                file.type,
            )
            click.echo("  " + file_path)


def _cli_print_grouped_file_trees(files: list[FileUseData], options: FileOptions) -> None:
    tree_root_files = [f for f in files if "SUITE" in f.type]

    if options.path_filter_glob:
        click.echo(
            NOTE_MARKER
            + f" Only showing trees for suite files matching '{options.path_filter_glob}'",
        )

        pattern = options.path_filter_glob.lower()
        tree_root_files = list(
            filter(
                lambda path: fnmatch.fnmatchcase(path.path_absolute.as_posix(), pattern),
                tree_root_files,
            ),
        )

    click.echo(
        f"Building {len(tree_root_files)} file import trees"
        + (f" with max depth {options.tree_max_depth}" if options.tree_max_depth >= 0 else "")
        + "...",
    )
    tree_builder = FileImportTreeBuilder(
        max_depth=options.tree_max_depth,
        max_height=options.tree_max_height,
    )
    grouped_trees = tree_builder.build_grouped_trees(tree_root_files, files)

    click.echo(f"Printing {len(grouped_trees)} tree groups...")
    for trees in grouped_trees:
        click.echo()
        for tree in trees[0:-1]:
            click.echo(normalize_file_path(tree.data.path_absolute))
        tree_builder.print_file_use_tree(trees[-1])


def _exit_code(files: list[FileUseData]) -> int:
    unused_files = [f for f in files if "SUITE" not in f.type and len(f.used_by) == 0]

    exit_code = len(unused_files)
    return min(exit_code, 200)
