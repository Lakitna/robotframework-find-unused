"""
Updates Readme based on CLI help texts.
"""

import re
from pathlib import Path

import click

from robotframework_find_unused.cli import cli

README_PATH = Path("./README.md")
PLACEHOLDER_MARKER = "UNRESOLVED_PLACEHOLDER"


def build_readme():
    """
    Update variable sections in readme
    """
    readme = _get_readme()
    readme = _remove_old_variable_content(readme)

    readme = _set_new_variable_content(
        readme,
        "command_keywords_cli_options",
        _get_command_params_table("keywords"),
    )
    readme = _set_new_variable_content(
        readme,
        "command_arguments_cli_options",
        _get_command_params_table("arguments"),
    )
    readme = _set_new_variable_content(
        readme,
        "command_variables_cli_options",
        _get_command_params_table("variables"),
    )
    readme = _set_new_variable_content(
        readme,
        "command_returns_cli_options",
        _get_command_params_table("returns"),
    )
    readme = _set_new_variable_content(
        readme,
        "command_files_cli_options",
        _get_command_params_table("files"),
    )

    _save_readme(readme + "\n")


def _remove_old_variable_content(content: str) -> str:
    active_var_area_name: str | None = None
    out_lines = []
    for line in content.splitlines():
        if active_var_area_name:
            if line != f"<!--</{active_var_area_name}>-->":
                continue

            out_lines.append(line)
            active_var_area_name = None
        else:
            if not line.startswith("<!--<"):
                out_lines.append(line)
                continue

            m = re.match(r"^<!--<([a-zA-Z_]+)>-->$", line)
            if not m:
                out_lines.append(line)
                continue

            out_lines.append(line)
            active_var_area_name = m.groups()[0]
            out_lines.append(f"[[{PLACEHOLDER_MARKER}:{active_var_area_name}]]")

    return "\n".join(out_lines)


def _set_new_variable_content(readme: str, variable: str, content: str) -> str:
    return readme.replace(
        f"[[{PLACEHOLDER_MARKER}:{variable}]]",
        content.strip(),
    )


def _get_readme() -> str:
    abs_path = README_PATH.resolve()
    with abs_path.open("r") as f:
        return f.read()


def _save_readme(content: str) -> None:
    abs_path = README_PATH.resolve()
    abs_path.write_text(content, encoding="utf-8")


def _get_command_params_table(command_name: str) -> str:
    command = cli.commands.get(command_name, None)
    if not command:
        msg = f"Unexpected command '{command_name}'"
        raise ValueError(msg)

    rows = [["flag", "option", "default", "description"]]
    for param in command.params:
        if param.param_type_name != "option":
            continue

        cols = []
        cols.append(", ".join([f"`{o}`" for o in param.opts]))
        cols.append(_get_command_options_col(command, param))
        cols.append(_get_command_default_col(param))
        cols.append(getattr(param, "help", "").replace("\n", " "))

        rows.append(cols)

    return _to_md_table(rows)


def _to_md_table(table: list[list[str]]) -> str:
    col_widths = []

    for row in table:
        for i, col in enumerate(row):
            if len(col_widths) < i + 1:
                col_widths.append(0)

            col_widths[i] = max(col_widths[i], len(col))

    table.insert(1, ["-" * w for w in col_widths])

    output = ""
    for row in table:
        line = "| "
        for col_i, col in enumerate(row):
            col_width = col_widths[col_i]
            line += col.ljust(col_width, " ")
            line += " | "

        line = line.strip()
        output += line + "\n"

    return output


def _get_command_options_col(command: click.Command, param: click.Parameter) -> str:  # noqa: C901, PLR0911
    param_type = param.type
    if isinstance(param_type, click.types.BoolParamType):
        return ""

    if isinstance(
        param_type,
        click.types.StringParamType | click.types.UnprocessedParamType,
    ):
        if param.metavar:
            return param.metavar

        return ""

    if isinstance(param_type, click.types.Choice):
        return " / ".join([f"`{c}`" for c in param_type.choices])

    if isinstance(param_type, click.types.IntRange):
        if getattr(param, "count", False) is True:
            return ""

        rng = param_type._describe_range()  # noqa: SLF001

        if param_type.min == 0 and param_type.min_open is False and param_type.max_open is True:
            return f"Positive integer ({rng})"
        if param_type.max == 0 and param_type.min_open is True and param_type.max_open is False:
            return f"Negative integer ({rng})"
        return f"Integer in range {rng}"

    if isinstance(param_type, click.types.IntParamType):
        if getattr(param, "count", False) is True:
            return ""

        return "Integer"

    msg = f"Unexpected parameter type '{param_type.name}' for command '{command.name}'."
    raise TypeError(msg)


def _get_command_default_col(param: click.Parameter) -> str:
    if (
        param.default is None
        or (isinstance(param.default, str | list) and len(param.default) == 0)
        or getattr(param, "count", False) is True
    ):
        return ""

    param_type = param.type
    if isinstance(param_type, click.types.BoolParamType):
        return ""

    return f"`{param.default}`"


if __name__ == "__main__":
    build_readme()
