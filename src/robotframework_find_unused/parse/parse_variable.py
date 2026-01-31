# Shortest possible var: `${x}`
MIN_VAR_CHAR_COUNT = 4


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
    while len(string) >= MIN_VAR_CHAR_COUNT and string[0:2] not in ["${", "&{", "@{", "%{"]:
        string = string[1:]

    if len(string) < MIN_VAR_CHAR_COUNT:
        return ""

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
