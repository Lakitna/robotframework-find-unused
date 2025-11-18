from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_keywords_command(self):
        self.run_test(
            ["keywords", "./robot"],
            "./expected_output.log",
            __file__,
            expected_exit_code=1,
        )

    def test_keywords_command_with_count(self):
        self.run_test(
            ["keywords", "./robot", "--show-count"],
            "./expected_output_count.log",
            __file__,
            expected_exit_code=1,
        )

    def test_keywords_command_with_verbose(self):
        self.run_test(
            ["keywords", "./robot", "--verbose"],
            "./expected_output_verbose.log",
            __file__,
            expected_exit_code=1,
        )
