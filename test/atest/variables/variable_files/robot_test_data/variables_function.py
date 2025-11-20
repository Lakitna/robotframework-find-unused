def get_variables():  # noqa: D103
    variables = {
        "static_var_from_python_function_file": True,
    }

    if True:
        variables["dynamic_var_from_python_function_file"] = True

    return variables
