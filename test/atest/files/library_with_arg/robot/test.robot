*** Settings ***
Library     Collections
Library     alpha.py    foo   bar    AS    AAA
Library     ./beta.py    AS    b
Library     Epsilon    AS    e
Resource    ./resource.resource


*** Test Cases ***
# Empty section
