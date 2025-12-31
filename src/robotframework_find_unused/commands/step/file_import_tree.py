"""
Implementation of the 'files' command
"""

from dataclasses import dataclass
from typing import Literal, Optional

import click

from robotframework_find_unused.common.cli import pretty_file_path
from robotframework_find_unused.common.const import FileUseData
from robotframework_find_unused.common.convert import to_relative_path
from robotframework_find_unused.common.normalize import normalize_file_path


@dataclass
class FileImportTreePrintLine:
    """Datastructure for printing file trees"""

    indent: int
    text: str
    color: str | None


@dataclass
class FileImportTreeNode:
    """Datastructure for file import trees"""

    data: FileUseData
    depth: int
    branches: list["FileImportTreeNode"] | Literal["CIRCULAR", "MAX_DEPTH", "DEDUPED"]
    parent: Optional["FileImportTreeNode"]

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

    def relative_path_to_parent(self) -> str:
        """
        Get relative file path from parent to self. Suitable for user output.
        """
        if self.parent is None:
            # No parent, return absolute path
            return normalize_file_path(self.data.path_absolute)

        return to_relative_path(
            self.parent.data.path_absolute.parent,
            self.data.path_absolute,
        )

    def __hash__(self) -> int:
        """Hash self and content"""
        return hash(hash(self.data) + self.content_hash())


class FileImportTreeBuilder:
    """Build and output file import trees."""

    max_height: int
    max_depth: int

    _tree_cache: dict[int, FileImportTreeNode]

    def __init__(self, max_depth: int = 5, max_height: int = -1) -> None:
        self.max_depth = max_depth
        self.max_height = max_height
        self._tree_cache = {}

    def build_grouped_trees(
        self,
        root_files: list[FileUseData],
        files: list[FileUseData],
    ) -> list[list[FileImportTreeNode]]:
        """
        Build file import trees for each root file. Group root files with identical imports.
        """
        file_imports_map = self.get_imports_of_files(files)

        grouped_trees: dict[int, list[FileImportTreeNode]] = {}
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
        visited_files_in_branch: list[str] | None = None,
        runtime_scope: set[str] | None = None,
    ) -> FileImportTreeNode:
        """
        Build file import tree for a single file.
        """
        if visited_files_in_branch is None:
            visited_files_in_branch = []
        if runtime_scope is None:
            runtime_scope = set()

        node = FileImportTreeNode(
            data=cur_file,
            depth=depth,
            branches=[],
            parent=None,
        )

        if self.max_depth > 0 and depth > self.max_depth:
            node.branches = "MAX_DEPTH"
            return node

        if cur_file.id in visited_files_in_branch:
            node.branches = "CIRCULAR"
            return node

        if cur_file.id in runtime_scope:
            node.branches = "DEDUPED"
            return node

        visited_files_in_branch = visited_files_in_branch.copy()
        visited_files_in_branch.append(cur_file.id)

        runtime_scope.add(cur_file.id)

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
                visited_files_in_branch=visited_files_in_branch,
                runtime_scope=runtime_scope,
            )
            branch_node.parent = node
            node.branches.append(branch_node)

        if depth == 0:
            self._tree_cache[cur_file_import_hash] = node
        return node

    def get_imports_of_files(self, files: list[FileUseData]) -> dict[str, list[FileUseData]]:
        """
        Swap nodes and branches from imported_files -> file to file -> imported_files.
        """
        file_imports_map: dict[str, list[FileUseData]] = {}
        for file in files:
            file_imports_map[file.id] = []

        for file in files:
            for using_file in file.used_by:
                file_imports_map[using_file.id].append(file)

        return file_imports_map

    def flatten_tree(self, tree: FileImportTreeNode) -> list[FileImportTreeNode]:
        """
        Flatten tree to list of nodes
        """
        nodes = []

        def recurse(node: FileImportTreeNode) -> None:
            nodes.append(node)

            for branch in node.branches:
                if not isinstance(branch, FileImportTreeNode):
                    continue
                recurse(branch)

        recurse(tree)
        return nodes

    def print_file_use_tree(self, tree: FileImportTreeNode):
        """
        Output the full tree to the user
        """
        nodes = self.flatten_tree(tree)

        if len(nodes) == 1:
            click.echo(
                click.style("No imports to show...", fg="bright_black"),
            )
            return

        print_nodes = nodes.copy()
        print_height = (
            min(self.max_height, len(print_nodes)) if self.max_height > 0 else len(print_nodes)
        )
        print_lines: list[FileImportTreePrintLine] = []
        while len(print_nodes) > 0:
            if len(print_lines) >= print_height:
                break

            node = print_nodes.pop(0)

            if isinstance(node.branches, str):
                self._print_pruned_node(node, print_lines)
                continue

            relative_path = node.relative_path_to_parent()
            types = node.data.type
            if len(types) == 0:
                print_lines.append(
                    FileImportTreePrintLine(
                        indent=node.depth,
                        text=f"{relative_path} [Unknown type]",
                        color="bright_red",
                    ),
                )
                continue

            print_lines.append(
                FileImportTreePrintLine(
                    indent=node.depth,
                    text=pretty_file_path(relative_path, node.data.type),
                    color=None,
                ),
            )

        for line in print_lines:
            indent = click.style("│  " * line.indent, fg="bright_black")
            text = click.style(line.text, fg=line.color) if line.color else line.text
            click.echo(indent + text)

        if len(print_nodes) > 0:
            click.echo(
                click.style(
                    f"Not showing {len(print_nodes)} additional files...",
                    fg="bright_black",
                ),
            )

        self._print_tree_summary(nodes)

    def _print_pruned_node(
        self,
        node: FileImportTreeNode,
        print_lines: list[FileImportTreePrintLine],
    ) -> None:
        relative_path = node.relative_path_to_parent()
        if node.branches == "CIRCULAR":
            print_lines.append(
                FileImportTreePrintLine(
                    indent=node.depth,
                    text=f"{relative_path} [Circular]",
                    color="yellow",
                ),
            )
            return
        if node.branches == "MAX_DEPTH":
            if print_lines[-1].text == "...":
                return

            print_lines.append(
                FileImportTreePrintLine(
                    indent=node.depth,
                    text="...",
                    color="bright_black",
                ),
            )
            return
        if node.branches == "DEDUPED":
            print_lines.append(
                FileImportTreePrintLine(
                    indent=node.depth,
                    text=f"{relative_path} [Already imported]",
                    color="bright_black",
                ),
            )
            return

        msg = f"Unexpected pruned branch reason '{node.branches}'"
        raise ValueError(msg)

    def _print_tree_summary(self, nodes: list[FileImportTreeNode]) -> None:
        stats: list[str] = self._get_tree_summary_stats(nodes)
        click.echo(click.style(" | ".join(stats), fg="bright_black"))

    def _get_tree_summary_stats(self, nodes: list[FileImportTreeNode]) -> list[str]:
        stats: list[str] = []

        height = len(nodes)
        stats.append(f"Tree height: {height}")

        max_depth = max(*[node.depth for node in nodes])
        if self.max_depth >= 0 and self.max_depth < max_depth:
            stats.append(f"Stats unreliable due to `--tree-max-depth {self.max_depth}`")
            return stats
        stats.append(f"Tree depth: {max_depth}")

        unique_file_count = len({node.data.id for node in nodes})
        stats.append(f"Unique files: {unique_file_count}")

        circular_count = len([node for node in nodes if node.branches == "CIRCULAR"])
        stats.append(f"Circular imports: {circular_count}")

        deduped_count = len([node for node in nodes if node.branches == "DEDUPED"])
        stats.append(f"Already imported: {deduped_count}")

        return stats
