*** Settings ***
Library     ./keywords.py


*** Test Cases ***
Call py keywords without using return
    # Does Not Return
    # Returning Keyword

Call builtin keywords without using return
    Get Variables
    Get Variable Value    foo
