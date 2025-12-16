"""
Implementation of the 'files' command
"""

from dataclasses import dataclass

import click

from robotframework_find_unused.common.cli import cli_hard_exit
from robotframework_find_unused.common.const import INDENT, WARN_MARKER, FileUseData
from robotframework_find_unused.common.normalize import normalize_file_path

from .step.discover_files import cli_discover_file_paths
from .step.file_import_tree import FileImportTreeBuilder
from .step.parse_file_use import cli_step_parse_file_use


@dataclass
class FileOptions:
    """
    Command line options for the 'files' command
    """

    path_filter_glob: str | None
    show_all_count: bool
    verbose: int
    source_path: str


def cli_files(options: FileOptions):
    """
    Entry point for the CLI command
    """
    file_paths = cli_discover_file_paths(options.source_path, verbose=options.verbose)
    if len(file_paths) == 0:
        return cli_hard_exit(options.verbose)

    files = cli_step_parse_file_use(file_paths, verbose=options.verbose)

    file_tree = _to_file_tree(files)
    # print(file_tree)

    # _cli_log_results(files, options)
    return 0


def _cli_log_results(files: list[FileUseData], options: FileOptions) -> None:
    for file in files:
        if file.type != "SUITE" and not file.used_by:
            click.echo("UNUSED " + str(file.path_absolute))
        else:
            click.echo(file.path_absolute)

        if len(file.type) == 0:
            click.echo(f"{INDENT}Used as: " + click.style("unknown", fg="bright_black"))
        elif len(file.type) == 1:
            file_type = next(iter(file.type))
            if file_type == "RESOURCE" and not str(file.path_absolute).endswith(".resource"):
                click.echo(f"{INDENT}{WARN_MARKER} .resource file unexpectedly used as {file_type}")
            elif file_type == "SUITE" and not str(file.path_absolute).endswith(".robot"):
                click.echo(f"{INDENT}{WARN_MARKER} .robot file unexpectedly used as {file_type}")
            elif file_type == "LIBRARY" and not str(file.path_absolute).endswith(".py"):
                click.echo(f"{INDENT}{WARN_MARKER} .py file unexpectedly used as {file_type}")
        else:
            click.echo(f"{INDENT}Used as: {' & '.join(file.type)}\t{WARN_MARKER}")

        click.echo(f"{INDENT}Use count: {len(file.used_by)}x")


def _to_file_tree(files: list[FileUseData]):
    # TODO: Make CLI args
    max_depth = 5
    max_height = 50

    tree_root_files = [f for f in files if "SUITE" in f.type]

    print(f"Building {len(tree_root_files)} trees with max depth {max_depth}")
    tree_builder = FileImportTreeBuilder(max_depth=max_depth)
    grouped_trees = tree_builder.build_grouped_trees(tree_root_files, files)

    print(f"Print {len(grouped_trees)} tree groups...")
    for trees in grouped_trees:
        click.echo()
        for tree in trees[0:-1]:
            click.echo(normalize_file_path(tree.data.path_absolute))
        tree_builder.print_file_use_tree(trees[-1], max_files=max_height)

    # return trees


def _exit_code(files: list[FileUseData]) -> int:
    print("TODO")

    exit_code = 0
    return min(exit_code, 200)
