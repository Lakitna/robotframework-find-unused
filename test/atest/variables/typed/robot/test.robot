*** Variables ***
${string_unused: str}             bar
${int_unused: int}                ${123}
${float_unused: float}            ${12.3}
@{list_unused: list[str]}         lorum    ipsum    dolor
&{dict_unused: dict[str, str]}    lorum=ipsum    dolor=amet
${dot: Secret}                       foo

${string_used: str}               bar
${int_used: int}                  ${123}
${float_used: float}              ${12.3}
@{list_used: list[str]}           lorum    ipsum    dolor
&{dict_used: dict[str, str]}      lorum=ipsum    dolor=amet
${dot.separated.used: str}        bar

# Nested vars
${abc}              abcdefg
${easyAs${abc}: str}     lorum


*** Test Cases ***
Set Variable In Test
    VAR    ${test_scope_var}    hello    scope=TEST
    VAR    ${suite_scope_var}    hello    scope=SUITE
    VAR    ${global_scope_var}    hello    scope=GLOBAL

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
