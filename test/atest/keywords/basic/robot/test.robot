*** Settings ***
Resource    ./keywords.resource

*** Test Cases ***
Call a custom keyword
    Amazing Keyword
    Undefined keyword


Empty setup and teardown
    No Operation

Using template
    [Documentation]
    ...  Test templates are unsupported:
    ...  `Test Template Keyword` and `Amazing Keyword` are uncounted
    [Template]    Test Template Keyword
    first test    Amazing Keyword
    second test    Amazing Keyword

*** Keywords ***
Test Template Keyword
    [Arguments]    ${some_data}    ${some_keyword}
    No Operation
