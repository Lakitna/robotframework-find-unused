from collections.abc import Iterable
from pathlib import Path

import click
import robot.errors
from robot.api.parsing import (
    File,
    KeywordSection,
    ModelVisitor,
    TestCaseSection,
    Variable,
    VariableSection,
    VariablesImport,
)

from robotframework_find_unused.common.const import (
    ERROR_MARKER,
    VariableData,
    VariableDefinedInType,
)
from robotframework_find_unused.common.impossible_state_error import ImpossibleStateError
from robotframework_find_unused.common.normalize import normalize_variable_name


class VariableDefinitionVisitor(ModelVisitor):
    """
    Visit file and discover variable definitions.
    """

    variables: dict[str, VariableData]
    current_working_file: Path | None = None
    current_working_directory: Path | None = None

    def __init__(self) -> None:
        self.variables = {}
        super().__init__()

    def visit_File(self, node: File):  # noqa: N802
        """Keep track of the current working file"""
        if node.source is not None:
            self.current_working_file = node.source
            self.current_working_directory = self.current_working_file.parent

        return self.generic_visit(node)

    def visit_VariableSection(self, node: VariableSection):  # noqa: N802
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

    def visit_VariablesImport(self, node: VariablesImport):  # noqa: N802
        """
        Look for variable declarations in variable files.
        """
        if self.current_working_directory is None:
            msg = "Found variables file import outside a .robot or .resource file"
            raise ImpossibleStateError(msg)

        import_path = node.name
        if "/" in import_path or "\\" in import_path:
            # Is a file path. Make it absolute
            import_path = self.current_working_directory.joinpath(node.name)

        try:
            self._import_variable_file(Path(import_path), node.args)
        except Exception as e:  # noqa: BLE001
            click.echo(f"{ERROR_MARKER} Failed to import variables from variables file.")
            click.echo(f"{ERROR_MARKER} Something went very wrong. Details below:")
            click.echo(f"{ERROR_MARKER} {e}")
            click.echo()

        return self.generic_visit(node)

    def visit_KeywordSection(self, _: KeywordSection):  # noqa: N802
        """Don't visit anything inside keyword sections. We don't need it"""
        return

    def visit_TestCaseSection(self, _: TestCaseSection):  # noqa: N802
        """Don't visit anything inside test case sections. We don't need it"""
        return

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
        name_normalized = normalize_variable_name(name)
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
            name=name,
            normalized_name=name_normalized,
            use_count=0,
            defined_in_type=defined_in_type,
            defined_in=defined_in.as_posix(),
            value=value,
        )
