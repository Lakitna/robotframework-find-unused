from pathlib import Path

import robot.parsing


def visit_files(
    file_paths: list[Path],
    visitor: robot.parsing.model.ModelVisitor,
):
    """
    Use Robocop to traverse files with a visitor.

    See Robocop/Robotframework docs on Visitor details.
    """
    for file_path in file_paths:
        model = robot.parsing.get_model(file_path, data_only=True)
        visitor.visit(model)
