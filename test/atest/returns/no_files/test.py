from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_returns_command_no_files(self):
        self.run_test(
            ["returns", "./robot"],
            "./expected_output.log",
            __file__,
            expected_exit_code=255,
        )

    def test_returns_command_no_files_verbose(self):
        self.run_test(
            ["returns", "./robot", "--verbose"],
            "./expected_output_verbose.log",
            __file__,
            expected_exit_code=255,
        )

    def test_returns_command_no_files_verbose_verbose(self):
        self.run_test(
            ["returns", "./robot", "--verbose", "--verbose"],
            "./expected_output_verbose_verbose.log",
            __file__,
            expected_exit_code=255,
        )
