*** Settings ***
Library     ./alpha.py    bar   foo    AS    Aaa
Library     ./alpha.py    AS    Bbb

*** Keywords ***
foo
    Import Library    beta.py    lorum
