*** Settings ***
Library     ./alpha.py    bar   foo    AS    Aaa
Library     ./alpha.py    AS    Bbb
Library     ./alpha.py    134  AS    BBB
Library     ./alpha.py    # no AS

*** Keywords ***
foo
    Import Library    beta.py    lorum
