*** Settings ***
Variables       ./variables.json
Variables       ${CURDIR}/variables.yaml
Variables       ./DynamicClassName.py    user_arg=True
Variables       StaticClassName.py
Variables       ./variables_function.py
Variables       ./variables_function_args.py    user_arg=True
Variables       robot_test_data.variables_module
Variables       ./variables_module_all.py


*** Variables ***
${var_from_robot_file}      ${True}


*** Test Cases ***
Use variable with extended syntax
    Log    ${list_var_from_json_file[0]}
    Log    ${dict_var_from_json_file.foo}
