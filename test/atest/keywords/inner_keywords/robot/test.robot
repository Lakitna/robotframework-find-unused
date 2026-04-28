*** Settings ***
Resource    ./keywords.resource


*** Test Cases ***
Call inner keywords
    Beautiful    Used as inner kw by Beautiful
    Beautiful    keywords.Used as inner kw by Beautiful
    Beautiful    inner_keyword=Used as inner kw by Beautiful
    Beautiful    inner_keyword=keywords.Used as inner kw by Beautiful
    Beautiful    UnknownLibrary.Unknown Keyword
    Beautiful    BuiltIn.Unknown Keyword
    Beautiful    BuiltIn.log    Log is a known keyword

Call multiple inner keywords with @args
    Run Keywords
    ...    Skip
    ...    BuiltIn.Skip
    ...    Skip
    ...    BuiltIn.Skip
    ...    Skip
    ...    BuiltIn.Skip

Using template
    [Template]    Amazing Test Template
    some data    Amazing Kw
    Amazing Kw    Amazing Kw


*** Keywords ***
Amazing Test Template
    [Arguments]    ${some_data}    ${some_keyword}
    No Operation
