*** Test Cases ***
Set Variable In Test
    # Unused
    VAR    ${no_scope_var_unused}    hello
    VAR    ${local_scope_var_unused}    hello    scope=LOCAL
    VAR    ${test_scope_var_unused}    hello    scope=TEST
    VAR    ${suite_scope_var_unused}    hello    scope=SUITE
    VAR    ${global_scope_var_unused}    hello    scope=GLOBAL
    ${test_local_var_keyword_unused}    Set Variable    hello
    Set Test Variable    ${test_scope_var_keyword_unused}    hello
    Set Suite Variable    ${suite_scope_var_keyword_unused}    hello
    Set Global Variable    ${global_scope_var_keyword_unused}    hello

    # Used
    VAR    ${no_scope_var_used}    hello
    VAR    ${local_scope_var_used}    hello    scope=LOCAL
    VAR    ${test_scope_var_used}    hello    scope=TEST
    VAR    ${suite_scope_var_used}    hello    scope=SUITE
    VAR    ${global_scope_var_used}    hello    scope=GLOBAL
    ${test_local_var_keyword_used}    Set Variable    hello
    Set Test Variable    ${test_scope_var_keyword_used}    hello
    Set Suite Variable    ${suite_scope_var_keyword_used}    hello
    Set Global Variable    ${global_scope_var_keyword_used}    hello

    Log    ${no_scope_var_used}
    Log    ${local_scope_var_used}
    Log    ${test_scope_var_used}
    Log    ${suite_scope_var_used}
    Log    ${global_scope_var_used}
    Log    ${test_local_var_keyword_used}
    Log    ${test_scope_var_keyword_used}
    Log    ${suite_scope_var_keyword_used}
    Log    ${global_scope_var_keyword_used}
