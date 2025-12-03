import sys
from typing import Literal

import click

from .const import NOTE_MARKER, VERBOSE_DOUBLE
from .gather_keywords import KeywordData


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


def cli_hard_exit(verbose: int) -> Literal[255]:
    """
    Immediately hard exit app. Use when something went wrong.
    """
    if verbose < VERBOSE_DOUBLE:
        click.echo(f"{NOTE_MARKER} Run with `--verbose --verbose` or `-vv` for more details")
    sys.exit(255)
    return 255
