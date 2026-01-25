from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_arguments_command(self):
        self.run_test(
            ["arguments", "./robot"],
            "./expected_output.log",
            __file__,
            expected_exit_code=2,
        )

    def test_arguments_command_with_count(self):
        self.run_test(
            ["arguments", "./robot", "--show-count"],
            "./expected_output_count.log",
            __file__,
            expected_exit_code=2,
        )

    def test_arguments_command_with_verbose(self):
        self.run_test(
            ["arguments", "./robot", "--verbose"],
            "./expected_output_verbose.log",
            __file__,
            expected_exit_code=2,
        )
