from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_arguments_command_data_driven(self):
        self.run_test(
            ["arguments", "./robot", "--show-count"],
            "./expected_output.log",
            __file__,
            expected_exit_code=2,
        )
