from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_variables_command_variable_files(self):
        self.run_test(
            ["variables", "./robot", "--show-count"],
            "./expected_output.log",
            __file__,
            expected_exit_code=20,
        )
