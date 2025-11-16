from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_keywords_command_no_files(self):
        self.run_test(
            ["keywords", "./robot"],
            "./expected_output.log",
            __file__,
            expected_exit_code=1_000_000,
        )

    def test_keywords_command_no_files_verbose(self):
        self.run_test(
            ["keywords", "./robot", "--verbose"],
            "./expected_output_verbose.log",
            __file__,
            expected_exit_code=1_000_000,
        )

    def test_keywords_command_no_files_verbose_verbose(self):
        self.run_test(
            ["keywords", "./robot", "--verbose", "--verbose"],
            "./expected_output_verbose_verbose.log",
            __file__,
            expected_exit_code=1_000_000,
        )
