class KeywordClass:
    def does_not_return_from_class(self) -> None:
        """Do nothing"""

    def returning_keyword_from_class(self):
        """Return true"""
        if True:
            return True
        return  # noqa: RET502
