*** Settings ***
Library     Collections
Library     Telnet    timeout=1s
Library     Telnet    timeout=10s
Library     CacheLibrary
Library     CacheLibrary    file_size_warning_bytes=1000
Library     alpha.py    foo    bar    AS    AAA
Library     ./beta.py    AS    b
Library     Epsilon    AS    e
Resource    ./resource.resource


*** Test Cases ***
# Empty section
