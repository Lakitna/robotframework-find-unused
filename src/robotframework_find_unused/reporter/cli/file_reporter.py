import fnmatch
import sys
from collections.abc import Generator
from pathlib import Path

import click

from robotframework_find_unused.commands.files.options import FileOptions
from robotframework_find_unused.commands.step.file_import_filter import cli_filter_file_imports
from robotframework_find_unused.commands.step.file_import_tree import FileImportTreeBuilder
from robotframework_find_unused.common.cli import pretty_file_path
from robotframework_find_unused.common.const import (
    DONE_MARKER,
    ERROR_MARKER,
    INDENT,
    NOTE_MARKER,
    VERBOSE_NO,
    VERBOSE_SINGLE,
    WARN_MARKER,
    FileUseData,
    FileUsedByData,
)
from robotframework_find_unused.common.normalize import normalize_file_path
from robotframework_find_unused.convert.convert_path import to_relative_path
from robotframework_find_unused.reporter.base.file_reporter import FileReporter

from .partial.discover_files import PartialCliReporterDiscoverFiles


class FileCliReporter(FileReporter, PartialCliReporterDiscoverFiles):
    """
    CLI reporter for files command.
    """

    def __init__(self, options: FileOptions) -> None:
        super().__init__(options)

    def on_count_file_uses_start(
        self,
        file_paths: list[Path],
        source_path: Path,
    ):
        """Before finding out which files are used"""
        click.echo("Parsing file imports...")

    def on_count_file_uses_end(
        self,
        file_paths: list[Path],
        source_path: Path,
        files: list[FileUseData],
    ):
        """When done counting file uses"""
        click.echo(f"{DONE_MARKER} Parsed {len(files)} files")

        if self.options.verbose == VERBOSE_NO:
            return

        file_types: dict[str, list[str]] = {}
        for file in files:
            file_type = "UNKNOWN" if len(file.type) == 0 else next(iter(file.type))

            if file_type not in file_types:
                file_types[file_type] = []
            file_types[file_type].append(file.id)

        sorted_file_types = sorted(
            file_types.items(),
            key=lambda x: len(x[1]),
            reverse=True,
        )
        for file_type, file_type_paths in sorted_file_types:
            click.echo(f"{INDENT}{len(file_type_paths)} files of type {file_type}")

            if self.options.verbose == VERBOSE_SINGLE:
                continue

            sorted_file_paths = sorted(file_type_paths, key=lambda f: f)
            for path in sorted_file_paths:
                click.echo(f"{INDENT}{INDENT}{click.style(path, fg='bright_black')}")

    def on_error(self, error: Exception):
        """When an error is raised"""
        click.echo(f"{ERROR_MARKER} {error}")

    def on_warn(self, warning: str):
        """When an warning is issues"""
        click.echo(f"{WARN_MARKER} {warning}")

    def on_command_end(self, files: list[FileUseData]):
        """When the command has done all the things"""
        self._cli_log_file_import_warnings(files)

        if self.options.show_tree:
            self._cli_print_grouped_file_trees(files)
        self._cli_log_results(files)

        unused_files = [f for f in files if "SUITE" not in f.type and len(f.used_by) == 0]
        exit_code = len(unused_files)
        sys.exit(min(exit_code, 200))

    def _cli_log_file_import_warnings(self, files: list[FileUseData]) -> None:
        cwd = Path.cwd().joinpath(self.options.source_path)

        file_count = 0
        log_lines = []
        for file in files:
            used_by_grouped_by_alias: dict[str | None, list[FileUsedByData]] = {}
            for used_by in file.used_by:
                if used_by.normalized_as_alias not in used_by_grouped_by_alias:
                    used_by_grouped_by_alias[used_by.normalized_as_alias] = []

                used_by_grouped_by_alias[used_by.normalized_as_alias].append(used_by)

            for used_by in used_by_grouped_by_alias.values():
                distinct_args = set()
                for f in used_by:
                    distinct_args.add(f.args)

                if len(distinct_args) <= 1:
                    # Never imported with different arguments
                    continue

                file_count += 1
                log_lines += list(
                    self._cli_log_file_import_warnings_lines_gen(
                        cwd,
                        file,
                        used_by,
                        distinct_args,
                    ),
                )
                log_lines.append("")

        if log_lines:
            # Remove trailing newline
            log_lines = log_lines[:-1]

            click.echo(
                f"{WARN_MARKER} {file_count} files used multiple times with different arguments:",
            )
            for line in log_lines:
                click.echo(line)

    def _cli_log_file_import_warnings_lines_gen(
        self,
        cwd: Path,
        file: FileUseData,
        used_by: list[FileUsedByData],
        distinct_args: set[tuple[str, ...]],
    ) -> Generator[str]:
        if len(used_by) == 0:
            return
        import_as_alias = used_by[0].as_alias

        file_path = pretty_file_path(to_relative_path(cwd, file.path_absolute), file.type)
        if import_as_alias:
            file_path += "  AS  " + import_as_alias
        yield f"{INDENT}Used file: {file_path}"

        yield f"{INDENT}With arguments:"
        for args in sorted(distinct_args):
            if len(args) == 0:
                yield click.style(f"{INDENT}{INDENT}[No arguments]", fg="bright_black")
            else:
                yield f"{INDENT}{INDENT}{'    '.join(args)}"

        if self.options.verbose == VERBOSE_NO:
            yield f"{INDENT}Used by {len(used_by)} files"
        else:
            yield f"{INDENT}Used by {len(used_by)} files:"
            used_by_files_sorted = sorted(
                used_by,
                key=lambda f: f.file.path_absolute.as_posix(),
            )
            for used_by_file in used_by_files_sorted:
                file_path = pretty_file_path(
                    to_relative_path(cwd, used_by_file.file.path_absolute),
                    used_by_file.file.type,
                )
                yield f"{INDENT}{INDENT}{file_path}"

    def _cli_log_results(self, files: list[FileUseData]) -> None:
        click.echo()

        files = [f for f in files if "SUITE" not in f.type]
        files = cli_filter_file_imports(
            files,
            filter_library=self.options.library_files,
            filter_variable=self.options.variable_files,
            filter_resource=self.options.resource_files,
            filter_unused=self.options.unused_files,
            filter_glob=self.options.path_filter_glob,
        )

        cwd = Path.cwd().joinpath(self.options.source_path)
        if self.options.show_all_count:
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

    def _cli_print_grouped_file_trees(self, files: list[FileUseData]) -> None:
        tree_root_files = [f for f in files if "SUITE" in f.type]

        if self.options.path_filter_glob:
            click.echo(
                NOTE_MARKER
                + f" Only showing trees for suite files matching '{self.options.path_filter_glob}'",
            )

            pattern = self.options.path_filter_glob.lower()
            tree_root_files = list(
                filter(
                    lambda path: fnmatch.fnmatchcase(path.path_absolute.as_posix(), pattern),
                    tree_root_files,
                ),
            )

        click.echo(
            f"Building {len(tree_root_files)} file import trees"
            + (
                f" with max depth {self.options.tree_max_depth}"
                if self.options.tree_max_depth >= 0
                else ""
            )
            + "...",
        )
        tree_builder = FileImportTreeBuilder(
            max_depth=self.options.tree_max_depth,
            max_height=self.options.tree_max_height,
        )
        grouped_trees = tree_builder.build_grouped_trees(tree_root_files, files)

        click.echo(f"Printing {len(grouped_trees)} tree groups...")
        for trees in grouped_trees:
            click.echo()
            for tree in trees[0:-1]:
                click.echo(normalize_file_path(tree.data.path_absolute))
            tree_builder.cli_file_use_tree(trees[-1])
