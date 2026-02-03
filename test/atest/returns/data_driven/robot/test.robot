*** Settings ***
Test Template       Template keyword


*** Test Cases ***
Test with template
    1
    2
    3
Another Test with template    4


*** Keywords ***
Template keyword
    [Arguments]    ${var}
    RETURN    ${var}
