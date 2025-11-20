class StaticClassName:
    class_var_from_python_class_file = True
    _excluded_var_from_python_class_file = True

    def __init__(self) -> None:
        self.static_init_var_from_python_class_file = "another value"
        if True:
            self.dynamic_init_var_from_python_class_file = "another value"
