"""
Implementation of the 'files' command
"""

from dataclasses import dataclass
from typing import Literal, Optional

import click

from robotframework_find_unused.common.const import FileUseData, FileUseType
from robotframework_find_unused.common.normalize import normalize_file_path


@dataclass
class TreeNode[T]:
    data: T
    depth: int
    branches: list["TreeNode[T]"] | Literal["CIRCULAR", "MAX_DEPTH", "DEDUPED"]
    parent: Optional["TreeNode[T]"]

    def content_hash(self) -> int:
        """
        Hash the content, but not itself.

        Use to find multiple nodes with same content.
        """
        if isinstance(self.branches, str):
            return hash(self.data)

        hashable = []
        for branch in self.branches:
            hashable.append(str(branch.content_hash()))
        return hash("|".join(hashable))

    def __hash__(self) -> int:
        return hash(hash(self.data) + self.content_hash())


class FileImportTreeBuilder:
    max_depth: int

    _tree_cache: dict[int, TreeNode]

    def __init__(self, max_depth: int = 5) -> None:
        self.max_depth = max_depth
        self._tree_cache = {}

    def build_grouped_trees(
        self,
        root_files: list[FileUseData],
        files: list[FileUseData],
    ) -> list[list[TreeNode[FileUseData]]]:
        """
        Build file import trees for each root file. Group root files with identical imports.
        """
        file_imports_map = self.get_imports_of_files(files)

        grouped_trees: dict[int, list[TreeNode[FileUseData]]] = {}
        for root_file in root_files:
            tree = self.build_single_file_tree(root_file, file_imports_map)

            tree_hash = tree.content_hash()
            if tree_hash not in grouped_trees:
                grouped_trees[tree_hash] = []
            grouped_trees[tree_hash].append(tree)

        return list(grouped_trees.values())

    def build_single_file_tree(
        self,
        cur_file: FileUseData,
        file_imports: dict[str, list[FileUseData]],
        *,
        depth: int = 0,
        visited_files: list[str] | None = None,
        scope: set[str] | None = None,
    ) -> TreeNode[FileUseData]:
        """
        Build file import tree for a single file.
        """
        if visited_files is None:
            visited_files = []
        if scope is None:
            scope = set()

        node = TreeNode[FileUseData](
            data=cur_file,
            depth=depth,
            branches=[],
            parent=None,
        )

        if depth > self.max_depth:
            node.branches = "MAX_DEPTH"
            return node

        if cur_file.id in visited_files:
            node.branches = "CIRCULAR"
            return node

        if cur_file.id in scope:
            node.branches = "DEDUPED"
            return node

        visited_files = visited_files.copy()
        visited_files.append(cur_file.id)

        scope.add(cur_file.id)

        cur_file_imports = file_imports.get(cur_file.id, [])

        cur_file_import_hash = hash("|".join([str(hash(i)) for i in cur_file_imports]))
        if depth == 0 and cur_file_import_hash in self._tree_cache:
            # We already built a tree with the same imports. Reuse the branches
            node.branches = self._tree_cache[cur_file_import_hash].branches
            return node

        node.branches = []
        for file_import in cur_file_imports:
            branch_node = self.build_single_file_tree(
                file_import,
                file_imports,
                depth=depth + 1,
                visited_files=visited_files,
                scope=scope,
            )
            branch_node.parent = node
            node.branches.append(branch_node)

        if depth == 0:
            self._tree_cache[cur_file_import_hash] = node
        return node

    def get_imports_of_files(self, files: list[FileUseData]) -> dict[str, list[FileUseData]]:
        file_imports_map: dict[str, list[FileUseData]] = {}
        for file in files:
            file_imports_map[file.id] = []

        for file in files:
            for using_file in file.used_by:
                file_imports_map[using_file.id].append(file)

        return file_imports_map

    def flatten_tree[T](self, tree: TreeNode[T]) -> list[TreeNode[T]]:
        nodes = []

        def recurse(node: TreeNode[T]) -> None:
            nodes.append(node)

            for branch in node.branches:
                if not isinstance(branch, TreeNode):
                    continue
                recurse(branch)

        recurse(tree)
        return nodes

    def print_file_use_tree(self, tree: TreeNode[FileUseData], *, max_files: int = 0):
        nodes = self.flatten_tree(tree)

        max_files = min(max_files, len(nodes)) if max_files > 0 else len(nodes)

        skip_max_depth = False
        for node in nodes[0:max_files]:
            indent = click.style("|  " * node.depth, fg="bright_black")

            relative_path = self._get_relative_path_to_parent(node)

            if isinstance(node.branches, str):
                if node.branches == "CIRCULAR":
                    click.echo(
                        indent
                        + click.style(
                            f"{relative_path} [Circular]",
                            fg="yellow",
                        ),
                    )
                if node.branches == "MAX_DEPTH" and not skip_max_depth:
                    click.echo(
                        indent
                        + click.style(
                            "...",
                            fg="bright_black",
                        ),
                    )
                    skip_max_depth = True
                if node.branches == "DEDUPED":
                    click.echo(
                        indent
                        + click.style(
                            f"{relative_path} [Already imported]",
                            fg="bright_black",
                        ),
                    )
                continue

            skip_max_depth = False

            types = node.data.type
            if len(types) > 1:
                click.echo(
                    click.style(
                        f"{relative_path} [Multi-type: {' & '.join(types)}]",
                        fg="bright_red",
                    ),
                )
            elif len(types) == 0:
                click.echo(
                    click.style(
                        f"{relative_path} [Unknown type]",
                        fg="bright_red",
                    ),
                )
            else:
                file_type = next(iter(node.data.type))
                click.echo(f"{indent}{self._pretty_file_path(relative_path, file_type)}")

        if len(nodes) > max_files:
            skipped_count = len(nodes) - max_files
            click.echo(
                click.style(
                    f"Not showing {skipped_count} additional files...",
                    fg="bright_black",
                ),
            )

    def _get_relative_path_to_parent(self, node: TreeNode[FileUseData]):
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

    def _pretty_file_path(self, path: str, file_type: FileUseType) -> str:
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
