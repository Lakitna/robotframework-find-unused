from robocop import Config, Robocop
from robocop.checkers import VisitorChecker


def visit_files_with_robocop(robocop_config: Config, visitor: VisitorChecker):
    """
    Use Robocop to traverse files with a visitor. See Robocop/Robotframework docs on Visitor
    details.
    """
    robocop = Robocop(config=robocop_config)
    robocop.recognize_file_types()

    for file, file_model in robocop.files.items():
        ast_node = file_model[1]
        visitor.scan_file(ast_node, file, None)
