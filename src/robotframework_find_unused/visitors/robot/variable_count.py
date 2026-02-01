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
from robotframework_find_unused.common.normalize import normalize_variable_name
from robotframework_find_unused.parse.parse_variable import get_variables_in_string
from robotframework_find_unused.resolve.resolve_variables import (
    SUPPORTED_BUILTIN_VARS,
    resolve_variable_name,
)


class RobotVisitorVariableUses(ModelVisitor):
    """
    Visit file and count variable usage.
    """

    variables: dict[str, VariableData]

    # Details: https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#special-variable-syntax
    _pattern_eval_variable = re.compile(r"\$(\w+)")
    # Details: https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#inline-python-evaluation
    _pattern_inline_eval = re.compile(r"\${{(.+?)}}")

    def __init__(self, variable_defs: dict[str, VariableData]) -> None:
        self.variables = variable_defs
        super().__init__()

    def visit_VariableSection(self, node: VariableSection):  # noqa: N802
        """
        Look for used variables in variable definitions.
        """
        for var_node in node.body:
            if not isinstance(var_node, Variable):
                continue
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
        for name in used_vars:
            self._count_variable_use(name)

    def _get_used_vars_in_eval(self, eval_str: str) -> list[str]:
        """
        Return a list of used variables in a given evaluated Python expression
        """
        eval_str = eval_str.strip()
        used_vars = self._get_used_vars_in_args([eval_str])

        match = self._pattern_eval_variable.findall(eval_str)
        for var in match:
            used_vars.append("${" + normalize_variable_name(var) + "}")

        return used_vars

    def _count_used_vars_in_args(self, args: Iterable[str]) -> None:
        """
        Count used variables found in a list of arguments
        """
        used_vars = self._get_used_vars_in_args(args)
        used_vars = self._filter_supported_vars(used_vars)
        for name in used_vars:
            self._count_variable_use(name)

    def _get_used_vars_in_args(self, args: Iterable[str]) -> list[str]:
        """
        Return a list of used variables in a given list of strings
        """
        used_vars = []
        for arg in args:
            var_match = get_variables_in_string(arg)
            used_vars += var_match

            eval_match = self._pattern_inline_eval.findall(arg)
            for inline_eval in eval_match:
                used_vars += self._get_used_vars_in_eval(inline_eval)

        return used_vars

    def _filter_supported_vars(self, variables: list[str]) -> list[str]:
        """
        Filter out unsupported variables and some Robot builtin stuff.
        """
        filtered = []
        for formatted_var in variables:
            var = normalize_variable_name(formatted_var)

            try:
                float(var)
                # Is a number, not a variable name.
                # Details: https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#number-variables
                continue
            except ValueError:
                pass

            if var in SUPPORTED_BUILTIN_VARS:
                continue

            (var, used_vars) = resolve_variable_name(var, self.variables)
            for v in used_vars:
                self._count_variable_use(v)

            if not var.isalnum():
                # Potential extended variable syntax
                var = self._normalize_extended_variable_syntax(var)

            filtered.append(var)

        return filtered

    def _normalize_extended_variable_syntax(self, var: str) -> str:
        if var in self.variables:
            return var

        var_name = var
        while len(var_name) > 0:
            # Remove all trailing alphanumeric
            while len(var_name) > 0 and var_name[-1].isalnum():
                var_name = var_name[0:-1]
            if len(var_name) == 0:
                break

            # Remove single trailing special char
            var_name = var_name[0:-1]
            if len(var_name) == 0:
                break

            if var_name in self.variables:
                return var_name

        # Could not find var. Don't modify.
        return var

    def _count_variable_use(self, normalized_name: str) -> None:
        """
        Count the variable.
        """
        if normalized_name not in self.variables:
            # Unknown variable definition. Ignore
            return
        self.variables[normalized_name].use_count += 1
