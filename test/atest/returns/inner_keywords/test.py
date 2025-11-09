from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_returns_command_with_inner_keywords(self):
        self.run_test(
            ["returns", "./robot", "--show-count"],
            "./expected_output.log",
            __file__,
        )
