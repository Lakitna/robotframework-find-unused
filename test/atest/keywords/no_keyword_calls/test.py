from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_keywords_command_with_no_keywords(self):
        self.run_test(
            ["keywords", "./robot", "--show-count"],
            "./expected_output.log",
            __file__,
        )
