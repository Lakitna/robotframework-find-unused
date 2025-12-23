from .const import VariableData
from .normalize import normalize_variable_name

supported_builtin_vars = {
    "true": "True",
    "false": "False",
    "none": "None",
    "empty": "",
    "space": " ",
}


def get_variables_in_string(input_string: str) -> list[str]:
    """
    Return the Robot variables in a string
    """
    variables: list[str] = []

    string = input_string
    while len(string) > 0:
        string = _find_variable_start(string)
        (string, variable) = _find_variable_end(string)

        if variable:
            variables.append(variable)

    return variables


def _find_variable_start(string: str) -> str:
    while len(string) > 0 and string[0] not in "$&@%":
        string = string[1:]
    return string


def _find_variable_end(string: str) -> tuple[str, str | None]:
    variable = ""
    depth = 0
    while len(string) > 0:
        char = string[0]
        if char == "{":
            depth += 1
        if char == "}":
            depth -= 1

        variable += char
        string = string[1:]

        if char == "}" and depth == 0:
            break

    return (string, variable or None)


def resolve_variables(
    robot_input: str,
    variables: dict[str, VariableData],
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
    if normalized_name in supported_builtin_vars:
        return supported_builtin_vars[normalized_name]

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
    var_name: str, variables: dict[str, VariableData]
) -> tuple[str, list[str]]:
    if not ("${" in var_name or "@{" in var_name or "&{" in var_name or "%{" in var_name):
        return (var_name, [])

    (resolved, resolved_vars) = resolve_variables(var_name, variables)
    if var_name == resolved:
        return (var_name, [])

    resolved_var = normalize_variable_name(resolved, strip_decoration=False)
    if resolved_var in variables:
        return (normalize_variable_name(resolved), resolved_vars)

    (recursed_resolved, recursed_resolved_vars) = resolve_variable_name(resolved, variables)
    return (recursed_resolved, resolved_vars + recursed_resolved_vars)
