*** Test Cases ***
Use some Arguments
    Keyword With Arguments    foo    optional_used=bar
    Keyword With Arguments    foo

*** Keywords ***
Keyword With Arguments
    [Arguments]    ${required}    ${optional_unsed}=${True}    ${optional_used}=${True}
    No Operation
