from pathlib import Path
from typing import TYPE_CHECKING, Literal

from robot.api.parsing import (
    ModelVisitor,
    TestCaseSection,
)

from robotframework_find_unused.common.const import FileUseData, FileUsedByData
from robotframework_find_unused.common.impossible_state_error import ImpossibleStateError
from robotframework_find_unused.common.normalize import normalize_file_path, normalize_keyword_name
from robotframework_find_unused.convert.convert_path import to_relative_path
from robotframework_find_unused.resolve.resolve_import_string import resolve_import_string

if TYPE_CHECKING:
    from robot.api.parsing import (
        File,
        KeywordCall,
        LibraryImport,
        ResourceImport,
        VariablesImport,
    )

    from robotframework_find_unused.reporter.base.file_reporter import FileReporter


class RobotVisitorFileImports(ModelVisitor):
    """
    Gather file imports
    """

    root_directory: Path
    discovered_files: set[Path]
    files: dict[str, FileUseData]
    init_files: dict[Path, FileUseData]
    current_working_file: FileUseData | None = None
    current_working_directory: Path | None = None

    def __init__(
        self,
        root_directory: Path,
        discovered_files: set[Path] | None,
        reporter: "FileReporter",
    ) -> None:
        self.root_directory = root_directory.absolute()
        self.discovered_files = discovered_files or set()
        self.reporter = reporter
        self.files = {}
        self.init_files = {}
        super().__init__()

    def visit_File(self, node: "File"):  # noqa: N802
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
            self.current_working_file = self._register_file(
                current_file_path_normalized,
                file_type,
                current_working_file,
            )

        return self.generic_visit(node)

    def _register_file(
        self,
        current_file_path_normalized: str,
        file_type: Literal["SUITE", "SUITE_INIT", "RESOURCE"],
        current_working_file: Path,
    ) -> FileUseData:
        """Register a file"""
        file = FileUseData(
            id=current_file_path_normalized,
            path_absolute=current_working_file,
            type={file_type},
            used_by=[],
        )

        if file_type == "SUITE_INIT":
            self.init_files[current_working_file.parent] = file

            # Assumption: Due to file path sorting, `__init__` is always processed before any suite
            # file it applies to.

        if file_type == "SUITE":
            self._register_use_of_suite_init(file)

        self.files[current_file_path_normalized] = file
        return file

    def _register_use_of_suite_init(self, file: FileUseData) -> None:
        """Register use of suite __init__ files"""
        if len(self.init_files) == 0:
            return

        root_dir_parts_len = len(self.root_directory.parts)

        path = file.path_absolute
        while len(path.parts) > root_dir_parts_len:
            path = path.parent
            init_file = self.init_files.get(path, None)

            if init_file:
                init_file.used_by.append(
                    FileUsedByData(
                        file=file,
                        as_alias=None,
                        normalized_as_alias=None,
                        args=(),
                    ),
                )

    def _get_file_type(
        self,
        file_node: "File",
        file_path: Path,
    ) -> Literal["SUITE", "SUITE_INIT", "RESOURCE"] | None:
        if file_path.stem == "__init__":
            return "SUITE_INIT"

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

    def visit_LibraryImport(self, node: "LibraryImport"):  # noqa: N802
        """Find out which libraries are actually used"""
        self._register_library_file(node.name, node.args, node.alias, import_type="Library")

    def _register_library_file(
        self,
        import_string: str,
        import_args: tuple[str, ...],
        import_as: str | None,
        import_type: Literal["Library", "Import Library"],
    ) -> None:
        lib_path = self._resolve_import_string(import_string, import_type=import_type)
        if lib_path:
            self._register_file_use(
                lib_path,
                import_args,
                import_as,
                file_type="LIBRARY",
            )

    def visit_ResourceImport(self, node: "ResourceImport"):  # noqa: N802
        """Find out which resource files are actually used"""
        self._register_resource_file(node.name, import_type="Resource")

    def _register_resource_file(
        self,
        import_string: str,
        import_type: Literal["Resource", "Import Resource"],
    ) -> None:
        resource_path = self._resolve_import_string(import_string, import_type=import_type)
        if resource_path:
            self._register_file_use(
                resource_path,
                import_args=(),
                import_as=None,
                file_type="RESOURCE",
            )

    def visit_VariablesImport(self, node: "VariablesImport"):  # noqa: N802
        """Find out which variable files are actually used"""
        self._register_variables_file(node.name, node.args, import_type="Variables")

    def _register_variables_file(
        self,
        import_string: str,
        import_args: tuple[str, ...],
        import_type: Literal["Variables", "Import Variables"],
    ) -> None:
        variables_path = self._resolve_import_string(import_string, import_type=import_type)
        if variables_path:
            self._register_file_use(
                variables_path,
                import_args,
                import_as=None,
                file_type="VARIABLE",
            )

    def visit_KeywordCall(self, node: "KeywordCall"):  # noqa: N802
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
            self._register_resource_file(
                import_string,
                import_type="Import Resource",
            )
        if keyword_name == "importlibrary":
            import_as = None
            args = node.args
            if len(args) >= 2 and "AS" in args:  # noqa: PLR2004
                import_as = args[-1]
                args = args[:-2]

            self._register_library_file(
                import_string,
                args,
                import_as,
                import_type="Import Library",
            )
        if keyword_name == "importvariables":
            self._register_variables_file(
                import_string,
                node.args,
                import_type="Import Variables",
            )

    def _register_file_use(
        self,
        file_path: Path,
        import_args: tuple[str, ...],
        import_as: str | None,
        file_type: Literal["RESOURCE", "LIBRARY", "VARIABLE"],
    ) -> None:
        if self.current_working_file is None:
            msg = "Registering import outside a .robot or .resource file"
            raise ImpossibleStateError(msg)

        file_path = file_path.resolve()
        normalized_path = normalize_file_path(file_path)
        normalized_import_as = normalize_keyword_name(import_as) if import_as else import_as

        file_used_by = FileUsedByData(
            file=self.current_working_file,
            as_alias=import_as,
            normalized_as_alias=normalized_import_as,
            args=import_args,
        )

        if normalized_path in self.files:
            existing = self.files[normalized_path]

            existing.type.add(file_type)
            existing.used_by.append(file_used_by)
            return

        self.files[normalized_path] = FileUseData(
            id=normalized_path,
            path_absolute=file_path,
            type={file_type},
            used_by=[file_used_by],
        )

    def _resolve_import_string(
        self,
        import_str: str,
        import_type: Literal[
            "Library",
            "Import Library",
            "Resource",
            "Import Resource",
            "Variables",
            "Import Variables",
        ],
    ) -> Path | None:
        if self.current_working_directory is None or self.current_working_file is None:
            msg = "Found import outside a .robot or .resource file"
            raise ImpossibleStateError(msg)

        try:
            return resolve_import_string(
                import_str,
                self.current_working_directory,
                self.root_directory,
                self.discovered_files,
            )
        except ImportError as e:
            from_path = to_relative_path(
                self.root_directory,
                self.current_working_file.path_absolute,
            )
            self.reporter.on_file_import_error(e, import_type, import_str, from_path)
