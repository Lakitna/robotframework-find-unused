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

Use some returns with embedded args keywords
    ${foo} =    Dreamy Keyword With Lorum Ipsum And Used Return
    ${bar} =    Dreamy Keyword With Dolor Sit And Used Return
    Dreamy Keyword With Amet Conscuer And Used Return

    Elegant Keyword With Foo bar-baz 123 And Unused Return

    ${baz} =    Fancy Keyword With _ And No Return
    Fancy Keyword With _ And No Return
