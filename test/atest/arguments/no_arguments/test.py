from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_arguments_command(self):
        self.run_test(
            ["arguments", "./robot"],
            "./expected_output.log",
            __file__,
            expected_exit_code=255,
        )
