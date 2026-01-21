*** Settings ***
Resource    alpha.resource


*** Test Cases ***
Some test
    Import Resource    ./beta.resource
    Import Variables    ./variable.py
