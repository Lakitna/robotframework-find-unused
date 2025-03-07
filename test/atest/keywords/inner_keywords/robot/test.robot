*** Settings ***
Library     BuiltIn
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
