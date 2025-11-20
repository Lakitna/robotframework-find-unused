import pytest
from robot.version import get_version

from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_keywords_command_keyword_hooks(self):
        if get_version()[0] == "6":
            pytest.skip("Robot 6 does not support keyword setup keywords")

        self.run_test(
            ["keywords", "./robot", "--show-count"],
            "./expected_output.log",
            __file__,
            expected_exit_code=1,
        )
