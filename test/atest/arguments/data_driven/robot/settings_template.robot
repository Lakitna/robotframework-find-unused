*** Settings ***
Test Template       Settings Template Keyword


*** Test Cases ***
Test with template
    1
    2
    3    ${False}
Another Test with template
    4    ${False}
    5


*** Keywords ***
Settings Template Keyword
    [Arguments]    ${var}    ${used_optional_var}=${True}    ${unused_optional_var}=${True}
    No operation
