*** Test Cases ***
Test with template
    [Template]    Test Template Keyword
    1
    2
    3

Another Test with template
    [Template]    Test Template Keyword
    4


*** Keywords ***
Test Template Keyword
    [Arguments]    ${var}
    No operation
