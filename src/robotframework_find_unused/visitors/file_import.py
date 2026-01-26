from pathlib import Path
from typing import Literal

import click
from robot.api.parsing import (
    File,
    KeywordCall,
    LibraryImport,
    ModelVisitor,
    ResourceImport,
    TestCaseSection,
    VariablesImport,
)

from robotframework_find_unused.common.const import ERROR_MARKER, FileUseData
from robotframework_find_unused.common.impossible_state_error import ImpossibleStateError
from robotframework_find_unused.common.normalize import normalize_file_path, normalize_keyword_name
from robotframework_find_unused.common.resolve_import_string import resolve_import_string


class FileImportVisitor(ModelVisitor):
    """
    Gather file imports
    """

    files: dict[str, FileUseData]
    current_working_file: FileUseData | None = None
    current_working_directory: Path | None = None

    def __init__(self) -> None:
        self.files = {}
        super().__init__()

    def visit_File(self, node: File):  # noqa: N802
        """Register the current file"""
        if node.source is None:
            return None

        current_working_file = node.source.resolve()
        self.current_working_directory = current_working_file.parent
        current_file_path_normalized = normalize_file_path(current_working_file)

        file_type = self._get_file_type(node, current_working_file)
        if file_type is None:
            return None

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

    def _get_file_type(
        self,
        file_node: File,
        file_path: Path,
    ) -> Literal["SUITE", "RESOURCE"] | None:
        file_extension = file_path.suffix.lstrip(".").lower()

        if file_extension == "robot":
            has_test_section = any(
                isinstance(section, TestCaseSection) for section in file_node.sections
            )
            if has_test_section:
                return "SUITE"

            # Assumption: .robot file used as resource file.
            return "RESOURCE"

        if file_extension == "resource":
            return "RESOURCE"

        return None

    def visit_LibraryImport(self, node: LibraryImport):  # noqa: N802
        """Find out which libraries are actually used"""
        self._register_library_file(node.name)

    def _register_library_file(self, import_string: str) -> None:
        lib_name = import_string
        if not lib_name.endswith(".py"):
            # Limitation: Importing a downloaded lib. We don't care.
            return

        lib_path = self._resolve_import_string(lib_name)

        # Limitation: No python module syntax

        self._register_file_use(lib_path, file_type="LIBRARY")

    def visit_ResourceImport(self, node: ResourceImport):  # noqa: N802
        """Find out which resource files are actually used"""
        self._register_resource_file(node.name)

    def _register_resource_file(self, import_string: str) -> None:
        resource_path = self._resolve_import_string(import_string)
        self._register_file_use(resource_path, file_type="RESOURCE")

    def visit_VariablesImport(self, node: VariablesImport):  # noqa: N802
        """Find out which variable files are actually used"""
        self._register_variables_file(node.name)

    def _register_variables_file(self, import_string: str) -> None:
        resource_path = self._resolve_import_string(import_string)
        self._register_file_use(resource_path, file_type="VARIABLE")

    def visit_KeywordCall(self, node: KeywordCall):  # noqa: N802
        """Find dynamic import keywords"""
        if not node.args:
            return

        import_string = node.args[0]
        if (
            "${" in import_string
            or "@{" in import_string
            or "%{" in import_string
            or "&{" in import_string
        ):
            # Limitation: Dynamic imports with variables are ignored
            return

        keyword_name = normalize_keyword_name(node.keyword)

        if keyword_name == "importresource":
            self._register_resource_file(import_string)
        if keyword_name == "importlibrary":
            self._register_library_file(import_string)
        if keyword_name == "importvariables":
            self._register_variables_file(import_string)

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

    def _resolve_import_string(self, import_str: str) -> Path:
        if self.current_working_directory is None:
            msg = "Found import outside a .robot or .resource file"
            raise ImpossibleStateError(msg)

        return resolve_import_string(import_str, self.current_working_directory)
