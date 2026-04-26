"""
CLI frontend
"""

from .arguments.arguments import command_arguments
from .arguments.options import ArgumentsOptions
from .files.files import command_files
from .files.options import FileOptions
from .keywords.keywords import command_keywords
from .keywords.options import KeywordOptions
from .returns.options import ReturnOptions
from .returns.returns import command_returns
from .variables.options import VariableOptions
from .variables.variables import command_variables

__all__ = [
    "ArgumentsOptions",
    "FileOptions",
    "KeywordOptions",
    "ReturnOptions",
    "VariableOptions",
    "command_arguments",
    "command_files",
    "command_keywords",
    "command_returns",
    "command_variables",
]
