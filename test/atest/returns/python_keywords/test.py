from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_returns_command_with_python_keywords(self):
        self.run_test(
            ["returns", "./robot", "--show-count", "--unused", "include"],
            "./expected_output.log",
            __file__,
            expected_exit_code=3,
        )
