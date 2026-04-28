*** Settings ***
Resource    ./keywords.resource


*** Test Cases ***
Call a custom keyword
    Amazing Keyword
    Undefined keyword
    Cute Keyword


*** Keywords ***
Cute Keyword
    No Operation
