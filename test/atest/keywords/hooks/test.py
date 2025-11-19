from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_keywords_command_hooks(self):
        self.run_test(
            ["keywords", "./robot", "--show-count"],
            "./expected_output.log",
            __file__,
            expected_exit_code=1,
        )
