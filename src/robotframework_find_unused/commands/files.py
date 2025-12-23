"""
Implementation of the 'files' command
"""

from dataclasses import dataclass
from pathlib import Path

import click

from robotframework_find_unused.common.cli import cli_hard_exit
from robotframework_find_unused.common.const import INDENT, WARN_MARKER, FileUseData, FileUseType
from robotframework_find_unused.common.convert import to_relative_path
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
    show_tree: bool
    tree_max_depth: int
    tree_max_height: int
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

    if options.show_tree:
        _cli_print_grouped_file_trees(files, options.tree_max_depth, options.tree_max_height)
    _cli_log_results(files, options)

    return 0


def _cli_log_results(files: list[FileUseData], options: FileOptions) -> None:
    click.echo()

    cwd = Path.cwd().joinpath(options.source_path)
    if options.show_all_count:
        # TODO: log filter
        non_suite_files = [f for f in files if "SUITE" not in f.type]
        sorted_files = sorted(non_suite_files, key=lambda f: f.id)
        sorted_files = sorted(sorted_files, key=lambda f: len(f.used_by))

        click.echo("import_count\tfile")
        for file in sorted_files:
            file_path = _pretty_file_path(
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
        # TODO: log filter
        unused_files = [f for f in sorted_files if "SUITE" not in f.type and len(f.used_by) == 0]

        if len(unused_files) == 0:
            click.echo("Found no unused files")
            return

        click.echo(f"Found {len(unused_files)} unused files:")
        for file in unused_files:
            file_path = _pretty_file_path(
                to_relative_path(cwd, file.path_absolute),
                file.type,
            )
            click.echo("  " + file_path)

    # for file in files:
    #     if file.type != "SUITE" and not file.used_by:
    #         click.echo("UNUSED " + str(file.path_absolute))
    #     else:
    #         click.echo(file.path_absolute)

    #     if len(file.type) == 0:
    #         click.echo(f"{INDENT}Used as: " + click.style("unknown", fg="bright_black"))
    #     elif len(file.type) == 1:
    #         file_type = next(iter(file.type))
    #         if file_type == "RESOURCE" and not str(file.path_absolute).endswith(".resource"):
    #             click.echo(f"{INDENT}{WARN_MARKER} .resource file unexpectedly used as {file_type}")
    #         elif file_type == "SUITE" and not str(file.path_absolute).endswith(".robot"):
    #             click.echo(f"{INDENT}{WARN_MARKER} .robot file unexpectedly used as {file_type}")
    #         elif file_type == "LIBRARY" and not str(file.path_absolute).endswith(".py"):
    #             click.echo(f"{INDENT}{WARN_MARKER} .py file unexpectedly used as {file_type}")
    #     else:
    #         click.echo(f"{INDENT}Used as: {' & '.join(file.type)}\t{WARN_MARKER}")

    #     click.echo(f"{INDENT}Use count: {len(file.used_by)}x")


def _cli_print_grouped_file_trees(
    files: list[FileUseData],
    max_depth: int,
    max_height: int,
) -> None:
    tree_root_files = [f for f in files if "SUITE" in f.type]

    click.echo(
        f"Building {len(tree_root_files)} file import trees"
        + (f" with max depth {max_depth}" if max_depth >= 0 else ""),
    )
    tree_builder = FileImportTreeBuilder(max_depth=max_depth, max_height=max_height)
    grouped_trees = tree_builder.build_grouped_trees(tree_root_files, files)

    click.echo(f"Print {len(grouped_trees)} tree groups...")
    for trees in grouped_trees:
        click.echo()
        for tree in trees[0:-1]:
            click.echo(normalize_file_path(tree.data.path_absolute))
        tree_builder.print_file_use_tree(trees[-1])


def _exit_code(files: list[FileUseData]) -> int:
    print("TODO")

    exit_code = 0
    return min(exit_code, 200)


# TODO: Move centrally
def _pretty_file_path(path: str, file_types: set[FileUseType]) -> str:
    if len(file_types) == 0:
        return path
    if len(file_types) > 1:
        return click.style(f"{path} [Used as: {' & '.join(file_types)}]", fg="yellow")

    file_type = next(iter(file_types))

    if file_type == "RESOURCE":
        return click.style(path, fg="bright_cyan")
    if file_type == "SUITE":
        return path
    if file_type == "LIBRARY":
        return click.style(path, fg="bright_magenta")
    if file_type == "VARIABLE":
        return click.style(path, fg="bright_green")

    msg = f"Unexpected file type {file_type}"
    raise ValueError(msg)
