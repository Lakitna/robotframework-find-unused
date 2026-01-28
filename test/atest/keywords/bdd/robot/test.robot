*** Settings ***
Resource    ./keywords.resource


*** Test Cases ***
Call a custom keyword
    Given Amazing Keyword
    When Undefined keyword
    And No Operation
    Then Beautiful Keyword
    But Log    hello
