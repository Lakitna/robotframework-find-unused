*** Settings ***
Resource    alpha.resource


*** Variables ***
${used_suite_variable}      bar
${unused_suite_variable}    bar


*** Test Cases ***
Use some Variables
    Log    ${used_suite_variable}

    Log    ${used_resource_variable}
    Log    ${used_resource_variable}

    Log    ${used_varfile_variable}
    Log    ${used_varfile_variable}
    Log    ${used_varfile_variable}
