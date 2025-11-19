def does_not_return() -> None:
    """Do nothing"""


def returning_keyword():
    """Return true"""
    if True:
        return True
    return  # noqa: RET502
