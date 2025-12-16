from pathlib import Path
from typing import Literal

import click
from robot.api.parsing import (
    File,
    LibraryImport,
    ModelVisitor,
    ResourceImport,
    VariablesImport,
)

from robotframework_find_unused.common.const import ERROR_MARKER, FileUseData
from robotframework_find_unused.common.impossible_state_error import ImpossibleStateError
from robotframework_find_unused.common.normalize import normalize_file_path


class FileImportVisitor(ModelVisitor):
    """
    Gather file imports
    """

    files: dict[str, FileUseData]
    current_working_file: FileUseData | None = None
    current_working_directory: Path | None = None

    def __init__(self, *, enrich_py_keywords: bool = False) -> None:
        self.enrich_py_keywords = enrich_py_keywords
        self.files = {}
        super().__init__()

    def visit_File(self, node: File):  # noqa: N802
        """Register the current file"""
        if node.source is None:
            return None

        current_working_file = node.source.resolve()
        self.current_working_directory = current_working_file.parent
        current_file_path_normalized = normalize_file_path(current_working_file)

        file_ext = current_working_file.suffix.lstrip(".").lower()
        if file_ext not in ["robot", "resource"]:
            return None

        file_type = "SUITE" if file_ext == "robot" else "RESOURCE"

        if current_file_path_normalized in self.files:
            # Already found as import
            self.current_working_file = self.files[current_file_path_normalized]
        else:
            self.current_working_file = FileUseData(
                normalize_file_path(current_working_file),
                path_absolute=current_working_file,
                type={file_type},
                used_by=[],
            )
            self.files[current_file_path_normalized] = self.current_working_file

        return self.generic_visit(node)

    def visit_LibraryImport(self, node: LibraryImport):  # noqa: N802
        """Find out which libraries are actually used"""
        if self.current_working_directory is None:
            msg = "Found library import outside a .robot or .resource file"
            raise ImpossibleStateError(msg)

        lib_name = node.name
        if not lib_name.endswith(".py"):
            # TODO: Limitation: No downloaded library imports
            # A downloaded lib. We don't care
            return
        if not lib_name.startswith(".") and "/" not in lib_name and "\\" not in lib_name:
            # Assume this is a downloaded library imported with `.py` postfix. We don't care
            return

        lib_path = self.current_working_directory.joinpath(lib_name)

        # TODO: Support name alias using `AS`
        # TODO: Limitation: No python module syntax

        self._register_file_use(lib_path, file_type="LIBRARY")

    def visit_ResourceImport(self, node: ResourceImport):  # noqa: N802
        """Find out which resource files are actually used"""
        if self.current_working_directory is None:
            msg = "Found resource import outside a .robot or .resource file"
            raise ImpossibleStateError(msg)

        resource_path = self.current_working_directory.joinpath(node.name)
        self._register_file_use(resource_path, file_type="RESOURCE")

    def visit_VariablesImport(self, node: VariablesImport):  # noqa: N802
        """Find out which variable files are actually used"""
        if self.current_working_directory is None:
            msg = "Found variables import outside a .robot or .resource file"
            raise ImpossibleStateError(msg)

        resource_path = self.current_working_directory.joinpath(node.name)
        self._register_file_use(resource_path, file_type="VARIABLE")

    def _register_file_use(
        self,
        file_path: Path,
        file_type: Literal["SUITE", "RESOURCE", "LIBRARY", "VARIABLE"],
    ) -> None:
        if self.current_working_file is None:
            msg = "Registering import outside a .robot or .resource file"
            raise ImpossibleStateError(msg)

        file_path = file_path.resolve()
        normalized_path = normalize_file_path(file_path)

        if normalized_path in self.files:
            existing = self.files[normalized_path]

            existing.type.add(file_type)
            existing.used_by.append(self.current_working_file)
            return

        if not file_path.exists():
            click.echo(
                f"{ERROR_MARKER} File does not exist. {normalized_path} "
                f"(imported from {normalize_file_path(self.current_working_file.path_absolute)})",
            )
            return

        self.files[normalized_path] = FileUseData(
            id=normalize_file_path(file_path),
            path_absolute=file_path,
            type={file_type},
            used_by=[self.current_working_file],
        )
