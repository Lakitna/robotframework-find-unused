*** Test Cases ***
Use some Arguments
    Keyword With Arguments    foo    optional_used=bar
    Keyword With Arguments    foo

    Keyword With Embed Arguments    foo    optional_used=bar
    Keyword With Embed Arguments    foo


*** Keywords ***
Keyword With Arguments
    [Arguments]    ${required}    ${optional_unsed}=${True}    ${optional_used}=${True}
    No Operation

Keyword With ${embedded} Arguments
    [Arguments]    ${required}    ${optional_unsed}=${True}    ${optional_used}=${True}
    No Operation
