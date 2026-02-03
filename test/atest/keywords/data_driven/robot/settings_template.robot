*** Settings ***
Test Template       Settings Template Keyword


*** Test Cases ***
Test with template
    1
    2
    3
Another Test with template    4


*** Keywords ***
Settings Template Keyword
    [Arguments]    ${var}
    No operation
