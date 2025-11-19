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
