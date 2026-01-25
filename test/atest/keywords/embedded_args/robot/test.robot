*** Settings ***
Resource    ./keywords.resource


*** Test Cases ***
Call keywords
    A Basic Beautiful Keyword
    A Basic 123 Keyword

    Keyword with Something or Another thing
    Keyword with Something and Another thing
    Keyword with Something and something specific

    Keyword without embedded args & some @ weird & characters % in it

    Unknown keyword
