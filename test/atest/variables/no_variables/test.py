from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_variables_command(self):
        self.run_test(
            ["variables", "./robot"],
            "./expected_output.log",
            __file__,
            expected_exit_code=1_000_000,
        )
