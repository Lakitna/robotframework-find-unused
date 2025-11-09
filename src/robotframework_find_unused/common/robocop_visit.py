import robot.parsing
from robocop.config import ConfigManager


def visit_files_with_robocop(
    robocop_config: ConfigManager,
    visitor: robot.parsing.model.ModelVisitor,
):
    """
    Use Robocop to traverse files with a visitor.

    See Robocop/Robotframework docs on Visitor details.
    """
    file_paths = (path for path, _config in robocop_config.paths)

    for file_path in file_paths:
        model = robot.parsing.get_model(file_path, data_only=True)
        visitor.visit(model)
