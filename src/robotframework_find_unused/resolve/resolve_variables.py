import os
from collections.abc import Mapping

from robotframework_find_unused.common.const import VariableValue
from robotframework_find_unused.common.normalize import normalize_variable_name
from robotframework_find_unused.parse.parse_variable import get_variables_in_string

# Limitation: No localisation
SUPPORTED_BUILTIN_VARS = {
    "true": "True",
    "false": "False",
    "none": "None",
    "null": "None",
    "empty": "",
    "space": " ",
    "/": os.sep,
    ":": os.pathsep,
    "\\n": os.linesep,
}


def resolve_variables(
    robot_input: str,
    variables: Mapping[str, VariableValue],
) -> tuple[str, list[str]]:
    """
    Resolve variables in the given string.

    Only resolves simple cases of builtin vars and given vars.
    """
    used_vars = get_variables_in_string(robot_input)

    replaced_vars: list[str] = []
    for var in used_vars:
        var_normalized = normalize_variable_name(var)
        val = None
        if var_normalized not in variables:
            try:
                val = _get_value_of_builtin_var(var_normalized)
            except ValueError:
                # Not known: Not simple. Don't try.
                continue

        if val is None:
            val = tuple(variables[var_normalized].value)
            if len(val) == 0:
                val = ""
            elif len(val) == 1:
                val = val[0]
            else:
                # Not single-line scalar: Not simple. Don't try.
                continue

        if val is not None:
            robot_input = robot_input.replace(var, val)
            replaced_vars.append(var_normalized)

    return (robot_input, replaced_vars)


def _get_value_of_builtin_var(normalized_name: str) -> str:
    if normalized_name in SUPPORTED_BUILTIN_VARS:
        return SUPPORTED_BUILTIN_VARS[normalized_name]

    stripped_var = normalized_name.removeprefix("{").removesuffix("}")
    try:
        float(stripped_var)
    except ValueError:
        pass
    else:
        # Is a number, not a variable name.
        return stripped_var

    msg = f"Can't get value of unsupported builtin variable '${normalized_name}'"
    raise ValueError(msg)


def resolve_variable_name(
    var_name: str,
    variables: Mapping[str, VariableValue],
) -> tuple[str, list[str]]:
    """
    Resolve variable name.

    Returns tuple of (resolved_var_name, used_vars)
    """
    if not ("${" in var_name or "@{" in var_name or "&{" in var_name or "%{" in var_name):
        return (var_name, [])

    (resolved, used_vars) = resolve_variables(var_name, variables)
    if var_name == resolved:
        return (var_name, [])

    resolved_var = normalize_variable_name(resolved, strip_decoration=False)
    if resolved_var in variables:
        return (normalize_variable_name(resolved), used_vars)

    (recursed_resolved, recursed_used_vars) = resolve_variable_name(resolved, variables)
    return (recursed_resolved, used_vars + recursed_used_vars)
