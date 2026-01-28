from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_keywords_bdd_command_with_count(self):
        self.run_test(
            ["keywords", "./robot", "--show-count", "--library", "include"],
            "./expected_output_count.log",
            __file__,
            expected_exit_code=0,
        )
