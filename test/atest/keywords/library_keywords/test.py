from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_keywords_command_with_library_keywords(self):
        self.run_test(
            ["keywords", "./robot", "--show-count", "--library", "include"],
            "./expected_output.log",
            __file__,
        )

    def test_keywords_command_with_library_keywords_and_verbose(self):
        self.run_test(
            ["keywords", "./robot", "--verbose", "--library", "include"],
            "./expected_output_verbose.log",
            __file__,
        )
