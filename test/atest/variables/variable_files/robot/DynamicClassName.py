class DynamicClassName:
    def get_variables(self, user_arg: bool = False):  # noqa: FBT001, FBT002
        variables = {
            "static_var_from_python_dynamic_class_file": True,
        }

        if True:
            variables["dynamic_var_from_python_dynamic_class_file"] = True

        if user_arg is not False:
            variables["dynamic_var_from_python_dynamic_class_file_using_user_args"] = True

        return variables
