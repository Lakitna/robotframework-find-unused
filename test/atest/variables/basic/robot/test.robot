*** Variables ***
${string_unused}            bar
${int_unused}               ${123}
${float_unused}             ${12.3}
@{list_unused}              lorum    ipsum    dolor
&{dict_unused}              lorum=ipsum    dolor=amet
${dot}                      foo

${string_used}              bar
${int_used}                 ${123}
${float_used}               ${12.3}
@{list_used}                lorum    ipsum    dolor
&{dict_used}                lorum=ipsum    dolor=amet
${dot.separated.used}       bar


*** Test Cases ***
Set Variable In Test
    # Unused
    ${test_local_var_keyword_unused}    Set Variable    hello
    Set Test Variable    ${test_scope_var_keyword_unused}    hello
    Set Suite Variable    ${suite_scope_var_keyword_unused}    hello
    Set Global Variable    ${global_scope_var_keyword_unused}    hello

    # Used
    ${test_local_var_keyword_used}    Set Variable    hello
    Set Test Variable    ${test_scope_var_keyword_used}    hello
    Set Suite Variable    ${suite_scope_var_keyword_used}    hello
    Set Global Variable    ${global_scope_var_keyword_used}    hello

    Log    ${test_local_var_keyword_used}
    Log    ${test_scope_var_keyword_used}
    Log    ${suite_scope_var_keyword_used}
    Log    ${global_scope_var_keyword_used}

Use some Variables
    Log    ${string_used}
    Log    ${int_used}
    Log    ${float_used}
    Log    @{list_used}
    Log    &{dict_used}

Use some Variables with extended syntax
    Log    ${i.do.not.exist}

    Log    ${dot.separated.used}
    Log    ${dot.separated.used.lower()}
    Log    ${string_used.extended}
    Log    ${string_used[0]}
    Log    ${string_used["extended"]}
    Log    ${list_used.extended}
    Log    ${list_used[0]}
    Log    ${list_used["extended"]}
    Log    ${dict_used.extended}
    Log    ${dict_used[0]}
    Log    ${dict_used["extended"]}
