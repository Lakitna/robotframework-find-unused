from dataclasses import dataclass
from typing import Literal, TypeAlias

import click
from robot.libdocpkg.model import ArgumentSpec

DONE_MARKER = "[ " + click.style("DONE", fg="green") + " ]"
INDENT = "    "

keyword_filter_option: TypeAlias = Literal["include", "exclude", "only"]


@dataclass
class KeywordData:
    name: str
    normalized_name: str
    type: Literal[
        "CUSTOM_SUITE", "CUSTOM_LIBRARY", "CUSTOM_RESOURCE", "LIBRARY", "UNKNOWN",
    ]
    argument_use_count: None | dict[str, int]
    deprecated: None | bool
    private: bool
    use_count: int
    returns: None | bool
    return_use_count: int
    arguments: ArgumentSpec | None
    library: str


@dataclass
class VariableData:
    name: str
    normalized_name: str
    name_without_brackets: str
    use_count: int
    defined_in_variables_section: bool


@dataclass
class LibraryData:
    name: str
    name_normalized: str
    keywords: list[KeywordData]
    keyword_names_normalized: set[str]
