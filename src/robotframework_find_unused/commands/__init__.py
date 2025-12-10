"""
CLI frontend
"""

from .arguments import ArgumentsOptions, cli_arguments
from .files import FileOptions, cli_files
from .keywords import KeywordOptions, cli_keywords
from .returns import ReturnOptions, cli_returns
from .variables import VariableOptions, cli_variables

__all__ = [
    "ArgumentsOptions",
    "FileOptions",
    "KeywordOptions",
    "ReturnOptions",
    "VariableOptions",
    "cli_arguments",
    "cli_files",
    "cli_keywords",
    "cli_returns",
    "cli_variables",
]
