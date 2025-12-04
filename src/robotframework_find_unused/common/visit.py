from pathlib import Path

import robot.api.parsing


def visit_robot_files(
    file_paths: list[Path],
    visitor: robot.api.parsing.ModelVisitor,
):
    """
    Use Robotframework to traverse files with a visitor.

    See Robotframework docs on Visitors for details.
    """
    for file_path in file_paths:
        model = robot.api.parsing.get_model(file_path, data_only=True)
        visitor.visit(model)
