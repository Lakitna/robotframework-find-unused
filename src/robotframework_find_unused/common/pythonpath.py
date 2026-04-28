import sys

from robot.conf import RobotSettings


def apply_pythonpath(pythonpath: list[str]):
    """Apply user-provided python path"""
    settings = RobotSettings({"pythonpath": pythonpath})

    if settings.pythonpath:
        sys.path = settings.pythonpath + sys.path
