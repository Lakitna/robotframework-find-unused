from pathlib import Path

import robot.api.parsing


def visit_files(
    file_paths: list[Path],
    visitor: robot.api.parsing.ModelVisitor,
):
    """
    Use Robocop to traverse files with a visitor.

    See Robocop/Robotframework docs on Visitor details.
    """
    for file_path in file_paths:
        model = robot.api.parsing.get_model(file_path, data_only=True)
        visitor.visit(model)
