from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_returns_command_data_driven(self):
        self.run_test(
            ["returns", "./robot", "--show-count"],
            "./expected_output.log",
            __file__,
            expected_exit_code=1,
        )
