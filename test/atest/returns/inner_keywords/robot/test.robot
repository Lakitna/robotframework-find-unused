*** Settings ***
Resource    ./keywords.resource


*** Test Cases ***
Call inner keywords
    Beautiful    Amazing Keyword With Return
    ${value} =    Beautiful    Amazing Keyword With Return
    ${value} =    Run Keyword    Amazing Keyword With Return
