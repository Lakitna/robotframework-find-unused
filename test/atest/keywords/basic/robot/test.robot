*** Settings ***
Resource    ./keywords.resource

Test Setup    Test Setup Keyword
Suite Setup    Suite Setup Keyword
Test Teardown    Test Teardown Keyword
Suite Teardown    Suite Teardown Keyword

*** Test Cases ***
Call a custom keyword
    [Setup]    Test Setup Keyword
    [Teardown]    Test Teardown Keyword
    Amazing Keyword
    Undefined keyword


Empty setup and teardown
    [Setup]
    [Teardown]
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
