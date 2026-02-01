import sys
from typing import Literal

import click

from .const import NOTE_MARKER, VERBOSE_DOUBLE, FileUseType, KeywordData, VariableData


def pretty_kw_name(keyword: KeywordData) -> str:
    """
    Format keyword name for output to the user
    """
    name = keyword.name

    if keyword.library:
        name = click.style(keyword.library + ".", fg="bright_black") + name

    if keyword.deprecated is True:
        name += " " + click.style("[DEPRECATED]", fg="red")

    return name


def pretty_file_path(path: str, file_types: set[FileUseType]) -> str:
    """
    Format file path for output to the user
    """
    if len(file_types) == 0:
        return path
    if len(file_types) > 1:
        return click.style(f"{path} [Used as: {' & '.join(file_types)}]", fg="yellow")

    file_type = next(iter(file_types))

    if file_type == "RESOURCE":
        return click.style(path, fg="bright_cyan")
    if file_type == "SUITE":
        return path
    if file_type == "SUITE_INIT":
        return path
    if file_type == "LIBRARY":
        return click.style(path, fg="bright_magenta")
    if file_type == "VARIABLE":
        return click.style(path, fg="bright_green")

    msg = f"Unexpected file type {file_type}"
    raise ValueError(msg)


def pretty_variable(var: VariableData) -> str:
    """
    Format variable for output to the user
    """
    out = var.name

    if var.type is not None:
        out = out.removesuffix("}")
        out += click.style(": " + var.type, fg="bright_black") + "}"

    if var.name != var.resolved_name:
        out += click.style(f" -> {var.resolved_name}", fg="bright_black")

    return out


def cli_hard_exit(verbose: int) -> Literal[255]:
    """
    Immediately hard exit app. Use when something went wrong.
    """
    if verbose < VERBOSE_DOUBLE:
        click.echo(f"{NOTE_MARKER} Run with `--verbose --verbose` or `-vv` for more details")
    sys.exit(255)
    return 255
