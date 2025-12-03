from dataclasses import dataclass
from typing import Literal, TypeAlias

import click
from robot.libdocpkg.model import ArgumentSpec

DONE_MARKER = "[ " + click.style("DONE", fg="green") + " ]"
WARN_MARKER = "[ " + click.style("WARNING", fg="yellow") + " ]"
ERROR_MARKER = "[ " + click.style("ERROR", fg="red") + " ]"
NOTE_MARKER = "[ " + click.style("NOTE", fg="cyan") + " ]"
INDENT = "    "
VERBOSE_NO = 0
VERBOSE_SINGLE = 1
VERBOSE_DOUBLE = 2

KeywordFilterOption: TypeAlias = Literal["include", "exclude", "only"]


@dataclass
class KeywordData:
    """Data structure for Keywords"""

    name: str
    normalized_name: str
    type: Literal[
        "CUSTOM_SUITE",
        "CUSTOM_LIBRARY",
        "CUSTOM_RESOURCE",
        "LIBRARY",
        "UNKNOWN",
    ]
    argument_use_count: None | dict[str, int]
    deprecated: None | bool
    private: bool
    use_count: int
    returns: None | bool
    """If True: Returns something. If False: Does not return anything. If None: Unknown"""

    return_use_count: int
    """If the keyword returns, how often is the return used during keyword call?"""

    arguments: ArgumentSpec | None
    library: str


@dataclass
class VariableData:
    """Data structure for Variables"""

    name: str
    normalized_name: str
    name_without_brackets: str
    use_count: int
    defined_in_variables_section: bool
    extended_syntaxable: bool


@dataclass
class LibraryData:
    """Data structure for Library keywords"""

    name: str
    name_normalized: str
    keywords: list[KeywordData]
    keyword_names_normalized: set[str]
