*** Settings ***
Library    Collections
Library    String

*** Test Cases ***
Call Library keywords
    Replace String    foo    search_for=f    replace_with=z
    XML.Element To String    <someElement />
