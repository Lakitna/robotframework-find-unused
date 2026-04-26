"""
Implementation of the 'variables' command
"""

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from robot.conf import RobotSettings

from robotframework_find_unused.commands.step.discover_files import step_discover_file_paths
from robotframework_find_unused.commands.step.variables_count_uses import step_count_variable_uses
from robotframework_find_unused.commands.step.variables_definitions import (
    step_get_variable_definitions,
)

if TYPE_CHECKING:
    from robotframework_find_unused.reporter.base.variable_reporter import VariableReporter

    from .options import VariableOptions


def command_variables(options: "VariableOptions", reporter: "VariableReporter") -> None:
    """
    Entry point for the CLI command 'variables'
    """
    reporter.on_command_start()

    settings = RobotSettings({"pythonpath": options.pythonpath})
    if settings.pythonpath:
        sys.path = settings.pythonpath + sys.path

    file_paths = step_discover_file_paths(options.source_path, reporter=reporter)
    if file_paths is None:
        return

    variables = step_get_variable_definitions(
        file_paths,
        Path(options.source_path),
        reporter=reporter,
    )
    if len(variables) == 0:
        return

    variables = step_count_variable_uses(
        file_paths,
        variables,
        reporter=reporter,
    )

    reporter.on_command_end(variables)
