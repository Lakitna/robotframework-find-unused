*** Settings ***
Variables       ./variables.json
Variables       ./variables.yaml
Variables       ./DynamicClassName.py    user_arg=True
Variables       ./StaticClassName.py
Variables       ./variables_function.py
Variables       ./variables_function_args.py    user_arg=True
Variables       ./variables_module.py
Variables       ./variables_module_all.py


*** Variables ***
${var_from_robot_file}      ${True}
