"""
Implementation of the 'files' command
"""

from typing import Literal, Optional
from pathlib import Path
from dataclasses import dataclass

import click

from robotframework_find_unused.common.cli import cli_hard_exit
from robotframework_find_unused.common.const import WARN_MARKER, INDENT, FileUseData, FileUseType
from robotframework_find_unused.common.normalize import normalize_file_path

from .step.discover_files import cli_discover_file_paths
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
    root_files = [f for f in files if "SUITE" in f.type]
    trees = []

    for root_file in root_files:
        if not root_file.path_absolute.as_posix().startswith(
            "C:/code/nlo/NLO.RFW.APPL/4_test_suite/eurojackpot/test/regression",
        ):
            continue
        tree = build_file_use_tree(root_file, files, max_depth=10)
        click.echo()

        print_file_use_tree(tree, max_files=50)
        # print_tree(tree)
        # trees.append(cli_print_tree(root_file, files, max_depth=5))
        # break

    return trees


@dataclass
class TreeNode[T]:
    data: T
    depth: int
    branches: list["TreeNode[T]"] | Literal["CIRCULAR", "MAX_DEPTH"]
    parent: Optional["TreeNode[T]"]


def build_file_use_tree(
    current_file: FileUseData,
    files: list[FileUseData],
    *,
    depth: int = 0,
    max_depth: int = 5,
    visited_nodes: list[Path] | None = None,
) -> TreeNode[FileUseData]:
    if visited_nodes is None:
        visited_nodes = []

    node = TreeNode[FileUseData](
        data=current_file,
        depth=depth,
        branches=[],
        parent=None,
    )

    if depth > max_depth:
        node.branches = "MAX_DEPTH"
        return node

    if current_file.path_absolute in visited_nodes:
        node.branches = "CIRCULAR"
        return node

    visited_nodes = visited_nodes.copy()
    visited_nodes.append(current_file.path_absolute)

    node.branches = []
    for file in files:
        used_by = [fd for fd in file.used_by if fd.path_absolute == current_file.path_absolute]
        if len(used_by) == 0:
            continue

        branch_node = build_file_use_tree(
            file,
            files,
            depth=depth + 1,
            max_depth=max_depth,
            visited_nodes=visited_nodes,
        )
        branch_node.parent = node
        node.branches.append(branch_node)

    return node


def flatten_tree[T](tree: TreeNode[T]) -> list[TreeNode[T]]:
    nodes = []

    def recurse(node: TreeNode[T]) -> None:
        nodes.append(node)

        for branch in node.branches:
            if not isinstance(branch, TreeNode):
                continue
            recurse(branch)

    recurse(tree)
    return nodes


def print_file_use_tree(tree: TreeNode[FileUseData], *, max_files=0):
    nodes = flatten_tree(tree)

    max_files = min(max_files, len(nodes)) if max_files > 0 else len(nodes)

    skip_max_depth = False
    for node in nodes[0:max_files]:
        indent = click.style("|  " * node.depth, fg="bright_black")

        relative_path = get_relative_path_to_parent(node)

        if isinstance(node.branches, str):
            if node.branches == "CIRCULAR":
                click.echo(indent + click.style(f"{relative_path} [Circular]", fg="yellow"))
            if node.branches == "MAX_DEPTH" and not skip_max_depth:
                click.echo(indent + click.style("...", fg="bright_black"))
                skip_max_depth = True
            continue

        skip_max_depth = False

        types = node.data.type
        if len(types) > 1:
            click.echo(click.style(f"{relative_path} [Multi-type: {' & '.join(types)}]", fg="red"))
        elif len(types) == 0:
            click.echo(click.style(f"{relative_path} [Unknown type]", fg="red"))
        else:
            file_type = next(iter(node.data.type))
            click.echo(f"{indent}{pretty_file_path(relative_path, file_type)}")

    if len(nodes) > max_files:
        skipped_count = len(nodes) - max_files
        click.echo(
            click.style(f"Not showing {skipped_count} additional files...", fg="bright_black")
        )


# def print_tree_recursive(node: TreeNode):
#     indent = click.style("|  " * node.depth, fg="bright_black")

#     relative_path = get_relative_path_to_parent(node)

#     if isinstance(node.branches, str):
#         if node.branches == "CIRCULAR":
#             click.echo(
#                 indent + click.style(f"{relative_path} [Circular]", fg="yellow"),
#             )
#         if node.branches == "MAX_DEPTH":
#             click.echo(
#                 indent + click.style("...", fg="bright_black"),
#             )
#             return False
#         return True

#     types = node.data.type
#     if len(types) > 1:
#         click.style(f"{relative_path} [Multi-type: {' & '.join(types)}]", fg="red")
#     elif len(types) == 0:
#         click.style(f"{relative_path} [Unknown type]", fg="red")
#     else:
#         file_type = next(iter(node.data.type))
#         click.echo(f"{indent}{pretty_file_path(relative_path, file_type)}")

#     for branch in node.branches:
#         cont = print_tree_recursive(branch)
#         if not cont:
#             break

#     return True


def get_relative_path_to_parent(node: TreeNode):
    if node.parent is None:
        # No parent, return absolute path
        return normalize_file_path(node.data.path_absolute)

    parent_path = node.parent.data.path_absolute

    relative_path = (
        node.data.path_absolute.resolve()
        .relative_to(parent_path.parent.resolve(), walk_up=True)
        .as_posix()
    )

    if not relative_path.startswith("."):
        relative_path = f"./{relative_path}"

    return relative_path


def pretty_file_path(path: str, file_type: FileUseType) -> str:
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


def _exit_code(files: list[FileUseData]) -> int:
    print("TODO")

    exit_code = 0
    return min(exit_code, 200)
