*** Settings ***
Test Template       Template keyword


*** Variables ***
${used_str}         str
${unused_str}       str


*** Test Cases ***
Test with template
    1    0    1
    5    ${used_str}    1
    3    1    1
    FOR    ${item}    IN RANGE    42
        ${item}    2nd arg
    END
    FOR    ${i}    IN RANGE    42
        ${used_str}    2nd arg
    END
Another Test with template    ${used_str}    1    5


*** Keywords ***
Template keyword
    [Arguments]    ${var}    @{arg}
    RETURN
