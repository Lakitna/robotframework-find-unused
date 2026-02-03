*** Test Cases ***
Test with template
    [Template]    Test Template Keyword
    1
    2
    3    ${False}

Another Test with template
    [Template]    Test Template Keyword
    4    ${False}
    5


*** Keywords ***
Test Template Keyword
    [Arguments]    ${var}    ${used_optional_var}=${True}    ${unused_optional_var}=${True}
    No operation
