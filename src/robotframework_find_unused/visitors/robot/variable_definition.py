from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING

import click
import robot.errors
from robot.api.parsing import (
    ModelVisitor,
    Variable,
)

from robotframework_find_unused.common.const import (
    ERROR_MARKER,
    VariableData,
    VariableDefinedInType,
)
from robotframework_find_unused.common.impossible_state_error import ImpossibleStateError
from robotframework_find_unused.common.normalize import (
    normalize_keyword_name,
    normalize_variable_name,
)
from robotframework_find_unused.convert.convert_path import to_relative_path
from robotframework_find_unused.resolve.resolve_import_string import resolve_import_string

if TYPE_CHECKING:
    from robot.api.parsing import (
        File,
        KeywordCall,
        Var,
        VariableSection,
        VariablesImport,
    )


class RobotVisitorVariableDefinitions(ModelVisitor):
    """
    Visit file and discover variable definitions.
    """

    root_directory: Path
    discovered_files: set[Path]
    variables: dict[str, VariableData]
    current_working_file: Path | None = None
    current_working_directory: Path | None = None

    def __init__(self, root_directory: Path, discovered_files: set[Path] | None = None) -> None:
        self.root_directory = root_directory.absolute()
        self.discovered_files = discovered_files or set()
        self.variables = {}
        super().__init__()

    def visit_File(self, node: "File"):  # noqa: N802
        """Keep track of the current working file"""
        if node.source is not None:
            self.current_working_file = node.source
            self.current_working_directory = self.current_working_file.parent

        return self.generic_visit(node)

    def visit_VariableSection(self, node: "VariableSection"):  # noqa: N802
        """
        Look for variable declarations in the variables section.
        """
        if self.current_working_file is None:
            msg = "Found variables section outside a .robot or .resource file"
            raise ImpossibleStateError(msg)

        for var_node in node.body:
            if not isinstance(var_node, Variable):
                continue

            self._register_variable(
                var_node.name,
                "variables_section",
                self.current_working_file,
                var_node.value,
            )

        return self.generic_visit(node)

    def visit_VariablesImport(self, node: "VariablesImport"):  # noqa: N802
        """
        Look for variable declarations in variable files.
        """
        if self.current_working_directory is None or self.current_working_file is None:
            msg = "Found variables file import outside a .robot or .resource file"
            raise ImpossibleStateError(msg)

        try:
            import_path = resolve_import_string(
                node.name,
                self.current_working_directory,
                self.root_directory,
                self.discovered_files,
            )
        except ImportError:
            from_path = to_relative_path(self.root_directory, self.current_working_file)
            click.echo(
                f"{ERROR_MARKER} `Variables  {node.name}` <- could not find. From {from_path}",
            )
            import_path = None

        if import_path:
            try:
                self._import_variable_file(Path(import_path), node.args)
            except Exception as e:  # noqa: BLE001
                click.echo(f"{ERROR_MARKER} Failed to import variables from variables file.")
                click.echo(f"{ERROR_MARKER} Something went very wrong. Details below:")
                click.echo(f"{ERROR_MARKER} {e}")
                click.echo()

        return self.generic_visit(node)

    def visit_KeywordCall(self, node: "KeywordCall"):  # noqa: N802
        """
        Look for variables set through specific builtin keywords.
        """
        kw_name = normalize_keyword_name(node.keyword)
        if kw_name not in ("settestvariable", "setsuitevariable", "setglobalvariable"):
            return

        if self.current_working_file is None:
            msg = "Found keyword call outside a .robot or .resource file"
            raise ImpossibleStateError(msg)

        (var_name, *var_value) = node.args
        self._register_variable(
            var_name,
            "runtime",
            self.current_working_file,
            var_value,
        )

    def visit_Var(self, node: "Var"):  # noqa: N802
        """
        Look for variables set through VAR syntax.
        """
        if not node.scope or node.scope.upper() == "LOCAL":
            return

        if self.current_working_file is None:
            msg = "Found VAR syntax outside a .robot or .resource file"
            raise ImpossibleStateError(msg)

        self._register_variable(
            node.name,
            "runtime",
            self.current_working_file,
            node.value,
        )

    def _import_variable_file(self, import_path: Path, import_args: tuple[str, ...]) -> None:
        """
        Import a file as a variable file.

        WARNING: This function uses code that is NOT in the public Robot API.
        Always wrap this function in a try-except to reduce the impact of internal Robot code
        changing.
        """
        from robot.variables.filesetter import VariableFileSetter
        from robot.variables.store import VariableStore

        var_store = VariableStore(None)
        file_setter = VariableFileSetter(var_store)

        try:
            file_setter.set(
                str(import_path),
                args=import_args,
            )
        except robot.errors.DataError as e:
            click.echo(f"{ERROR_MARKER} {e.message.splitlines()[0]}")
            return

        for var_name in var_store.as_dict(decoration=True):
            self._register_variable(var_name, "variable_file", import_path, [])

    def _register_variable(
        self,
        name: str,
        defined_in_type: VariableDefinedInType,
        defined_in: Path,
        value: Iterable[str],
    ) -> None:
        (var_name, var_type) = self._parse_var_name(name)

        name_normalized = normalize_variable_name(var_name)
        if name_normalized in self.variables:
            var_def = self.variables[name_normalized]

            if var_def.defined_in_type in (
                "variables_section",
                "variable_file",
            ):
                # Existing def is from primary source. Keep
                return

            if var_def.defined_in_type == defined_in_type:
                # Existing def is from equal source. Keep
                return

        self.variables[name_normalized] = VariableData(
            name=var_name,
            type=var_type,
            normalized_name=name_normalized,
            resolved_name=var_name,
            use_count=0,
            defined_in_type=defined_in_type,
            defined_in=defined_in.as_posix(),
            value=value,
        )

    def _parse_var_name(self, name: str) -> tuple[str, str | None]:
        if ": " not in name:
            return (name, None)

        (var_name, var_type) = name.split(": ")
        var_name = var_name + "}"
        var_type = var_type.removesuffix("}")
        return (var_name, var_type)
