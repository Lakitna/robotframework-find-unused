def get_variables(user_arg: bool = False):  # noqa: D103, FBT001, FBT002
    variables = {
        "static_var_from_python_function_file_using_user_args": True,
    }

    if user_arg is not False:
        variables["dynamic_var_from_python_function_file_using_user_args"] = True

    return variables
