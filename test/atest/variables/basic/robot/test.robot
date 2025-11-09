*** Variables ***
${string_unused}     bar
${int_unused}     ${123}
${float_unused}     ${12.3}
@{list_unused}     lorum     ipsum    dolor
&{dict_unused}     lorum=ipsum    dolor=amet

${string_used}     bar
${int_used}     ${123}
${float_used}     ${12.3}
@{list_used}     lorum     ipsum    dolor
&{dict_used}     lorum=ipsum    dolor=amet

*** Test Cases ***
Set Variable In Test
    VAR  ${test_scope_var}    hello    scope=TEST
    VAR  ${suite_scope_var}    hello    scope=SUITE
    VAR  ${global_scope_var}    hello    scope=GLOBAL

Use some Variables
    Log    ${string_used}
    Log    ${int_used}
    Log    ${float_used}
    Log    @{list_used}
    Log    &{dict_used}
