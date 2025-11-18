from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_variables_command(self):
        self.run_test(
            ["variables", "./robot"],
            "./expected_output.log",
            __file__,
            expected_exit_code=5,
        )

    def test_variables_command_with_count(self):
        self.run_test(
            ["variables", "./robot", "--show-count"],
            "./expected_output_count.log",
            __file__,
            expected_exit_code=5,
        )

    def test_variables_command_with_verbose(self):
        self.run_test(
            ["variables", "./robot", "--verbose"],
            "./expected_output_verbose.log",
            __file__,
            expected_exit_code=5,
        )
