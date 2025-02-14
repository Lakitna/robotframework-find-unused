from robocop import Config

from robotframework_find_unused.common.robocop_visit import visit_files_with_robocop
from robotframework_find_unused.visitors.variable import VariableVisitor


def count_variable_uses(robocop_config: Config):
    """
    Walk through all robot files with RoboCop to count keyword uses.
    """
    visitor = VariableVisitor()
    visit_files_with_robocop(robocop_config, visitor)

    variables = [v for v in visitor.variables.values() if v.defined_in_variables_section == True]
    return variables
