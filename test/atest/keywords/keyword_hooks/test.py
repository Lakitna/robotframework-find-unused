from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_keywords_command_keyword_hooks(self):
        self.run_test(
            ["keywords", "./robot", "--show-count"],
            "./expected_output.log",
            __file__,
            expected_exit_code=1,
            # Robot 6 does not support keyword setup keywords
            min_robot_version="7.0.0",
        )
