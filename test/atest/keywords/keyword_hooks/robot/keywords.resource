*** Keywords ***
Keyword Setup Keyword
    No Operation

Keyword Teardown Keyword
    No Operation

Amazing Keyword
    [Setup]    Keyword Setup Keyword
    No Operation
    [Teardown]    Keyword Teardown Keyword

Beautiful Keyword
    [Setup]
    Amazing Keyword
    [Teardown]
