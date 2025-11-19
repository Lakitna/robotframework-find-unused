import re
from collections.abc import Iterable

from robot.api.parsing import (
    Arguments,
    For,
    If,
    KeywordCall,
    ModelVisitor,
    Variable,
    VariableSection,
)

from robotframework_find_unused.common.const import VariableData


class VariableVisitor(ModelVisitor):
    """
    Visit and count variable usage.

    A Robocop visitor. Will never log a lint issue, unlike a normal Robocop visitor. We use it here
    as a convenient way of working with Robotframework files.

    Uses file exclusion from the Robocop config.

    Gathers variable defintions
    Counts variable usage
    """

    variables: dict[str, VariableData]

    _pattern_variable = re.compile(r"[@$&](\{[^{].+?[^}]\})")
    # Details: https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#special-variable-syntax
    _pattern_eval_variable = re.compile(r"\$(\w+)")
    # Details: https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#inline-python-evaluation
    _pattern_inline_eval = re.compile(r"\${{(.+?)}}")

    def __init__(self) -> None:
        self.variables = {}
        super().__init__()

    def visit_VariableSection(self, node: VariableSection):  # noqa: N802
        """
        Look for variable declarations in the variables section.

        Look for used variables in variable definitions.
        """
        for var_node in node.body:
            if not isinstance(var_node, Variable):
                continue

            name = self._normalize_var_name(var_node.name)
            if name not in self.variables:
                # Set defined variable to be unused
                self.variables[name] = VariableData(
                    name=var_node.name,
                    normalized_name=name,
                    name_without_brackets=self._var_name_without_brackets(
                        var_node.name,
                    ),
                    use_count=0,
                    defined_in_variables_section=True,
                )
            else:
                self.variables[name].defined_in_variables_section = True
                self.variables[name].name = var_node.name

            self._count_used_vars_in_args(var_node.value)

        return self.generic_visit(node)

    def visit_Arguments(self, node: Arguments):  # noqa: N802
        """
        Look for used variables in the default value of keyword arguments.
        """
        arguments = node.values

        for argument in arguments:
            if "=" not in argument:
                # Argument has no default. We don't care about it.
                continue

            argument_default = argument.split("=", 1)[1]
            self._count_used_vars_in_args([argument_default])

        return self.generic_visit(node)

    def visit_KeywordCall(self, node: KeywordCall):  # noqa: N802
        """
        Look for used variables called keyword arguments.
        """
        if node.keyword.lower() == "evaluate":
            self._count_used_vars_in_eval(node.args[0])
        else:
            self._count_used_vars_in_args(node.args)

        return self.generic_visit(node)

    def visit_For(self, node: For):  # pyright: ignore[reportIncompatibleMethodOverride] # noqa: N802
        """
        Look for used variables in for loop conditions.
        """
        self._count_used_vars_in_args(node.values)

        return self.generic_visit(node)

    def visit_If(self, node: If):  # pyright: ignore[reportIncompatibleMethodOverride] # noqa: N802
        """
        Look for used variables in if/else/elseif statement conditions.
        """
        if node.condition:
            self._count_used_vars_in_eval(node.condition)

        return self.generic_visit(node)

    def _count_used_vars_in_eval(self, eval_str: str) -> None:
        """
        Count used variables found in a python evaluation context
        """
        used_vars = self._get_used_vars_in_eval(eval_str)
        used_vars = self._filter_supported_vars(used_vars)
        for name, formatted_name in used_vars:
            self._count_variable_use(name, formatted_name)

    def _get_used_vars_in_eval(self, eval_str: str) -> list[str]:
        """
        Return a list of used variables in a given evaluated Python expression
        """
        eval_str = eval_str.strip()
        used_vars = self._get_used_vars_in_args([eval_str])

        match = self._pattern_eval_variable.findall(eval_str)
        for var in match:
            used_vars.append(self._normalize_var_name("${" + var + "}"))

        return used_vars

    def _count_used_vars_in_args(self, args: Iterable[str]) -> None:
        """
        Count used variables found in a list of arguments
        """
        used_vars = self._get_used_vars_in_args(args)
        used_vars = self._filter_supported_vars(used_vars)
        for name, formatted_name in used_vars:
            self._count_variable_use(name, formatted_name)

    def _get_used_vars_in_args(self, args: Iterable[str]) -> list[str]:
        """
        Return a list of used variables in a given list of strings
        """
        used_vars = []
        for arg in args:
            var_match = self._pattern_variable.findall(arg)
            used_vars += var_match

            eval_match = self._pattern_inline_eval.findall(arg)
            for inline_eval in eval_match:
                used_vars += self._get_used_vars_in_eval(inline_eval)

        return used_vars

    def _filter_supported_vars(self, variables: list[str]) -> list[tuple[str, str]]:
        """
        Filter out unsupported variables and some Robot builtin stuff.
        """
        filtered = []
        for formatted_var in variables:
            var = self._normalize_var_name(formatted_var)

            if "${" in var or "@{" in var or "&{" in var:
                # There is a variable inside the variable name.
                # Not worth supporting this at this time
                continue

            try:
                float(var.strip("{}"))
                # Is a number, not a variable name.
                # Details: https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#number-variables
                continue
            except ValueError:
                pass

            if var in ("{true}", "{false}", "{none}", "{empty}", "{space}"):
                continue

            filtered.append(
                (var, formatted_var),
            )

        return filtered

    def _normalize_var_name(self, name: str) -> str:
        return name.lstrip("$@&").replace(" ", "").replace("_", "").lower()

    def _var_name_without_brackets(self, name: str) -> str:
        return name.lstrip("$@&").strip("{}")

    def _count_variable_use(self, normalized_name: str, name: str) -> None:
        """
        Count the variable.
        """
        if normalized_name not in self.variables:
            self.variables[normalized_name] = VariableData(
                name=name,
                normalized_name=normalized_name,
                name_without_brackets=self._var_name_without_brackets(name),
                use_count=0,
                defined_in_variables_section=False,
            )
        self.variables[normalized_name].use_count += 1
