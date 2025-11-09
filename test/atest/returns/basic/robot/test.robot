*** Settings ***
Resource    ./keywords.resource

*** Test Cases ***
Use some returns
    ${foo} =    Amazing Keyword With Used Return
    ${bar} =    Amazing Keyword With Used Return
    Amazing Keyword With Used Return

    Beautiful Keyword With Unused Return

    ${baz} =    Cute Keyword Without Return
    Cute Keyword Without Return
