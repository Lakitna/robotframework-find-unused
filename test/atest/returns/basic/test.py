from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_returns_command(self):
        self.run_test(
            ["returns", "./robot"],
            "./expected_output.log",
            __file__,
            expected_exit_code=2,
        )

    def test_returns_command_with_count(self):
        self.run_test(
            ["returns", "./robot", "--show-count"],
            "./expected_output_count.log",
            __file__,
            expected_exit_code=2,
        )

    def test_returns_command_with_verbose(self):
        self.run_test(
            ["returns", "./robot", "--verbose"],
            "./expected_output_verbose.log",
            __file__,
            expected_exit_code=2,
        )
