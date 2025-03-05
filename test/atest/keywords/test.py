from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_keywords_command(self):
        self.run_test(
            ["keywords", "./robot"],
            "./expected_output.log",
            __file__,
        )
