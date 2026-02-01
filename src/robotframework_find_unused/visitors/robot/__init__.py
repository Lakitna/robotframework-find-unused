"""
Robot Framework AST visitors
"""

from pathlib import Path
from typing import Literal

import robot.api.parsing

from robotframework_find_unused.parse.parse_robot_file import RobotFileSectionName, parse_robot_file


def visit_robot_files(
    file_paths: list[Path],
    visitor: robot.api.parsing.ModelVisitor,
    parse_sections: tuple[RobotFileSectionName, ...] | Literal["all"] = "all",
):
    """
    Use Robotframework to traverse files with a visitor.

    See Robotframework docs on Visitors for details.
    """
    for file_path in file_paths:
        model = parse_robot_file(file_path, parse_sections)
        visitor.visit(model)
