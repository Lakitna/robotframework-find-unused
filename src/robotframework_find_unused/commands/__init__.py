"""
CLI frontend
"""

from .arguments import ArgumentsOptions, command_arguments
from .files import FileOptions, command_files
from .keywords import KeywordOptions, command_keywords
from .returns import ReturnOptions, command_returns
from .variables import VariableOptions, command_variables

__all__ = [
    "ArgumentsOptions",
    "FileOptions",
    "KeywordOptions",
    "ReturnOptions",
    "VariableOptions",
    "command_arguments",
    "command_keywords",
    "command_returns",
    "command_variables",
    "command_files",
]
