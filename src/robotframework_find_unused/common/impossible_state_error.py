ISSUE_TRACKER_URL = "https://github.com/Lakitna/robotframework-find-unused/issues"


class ImpossibleStateError(Exception):
    """
    Exception for things that should not be possible.

    This error being raised means that something went horribly wrong somewhere.
    """

    def __init__(self, message: str) -> None:
        message = (
            message
            + " - This should be impossible. Please open an issue at "
            + ISSUE_TRACKER_URL
            + " and let us know how you managed to do this."
        )
        super().__init__(message)
