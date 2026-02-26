from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_files_command_library(self):
        self.run_test(
            ["files", "./robot", "--pythonpath", "./robot"],
            "./expected_output.log",
            __file__,
            expected_exit_code=1,
        )

    def test_files_command_library_tree(self):
        self.run_test(
            ["files", "./robot", "--show-tree", "--pythonpath", "./robot"],
            "./expected_output_tree.log",
            __file__,
            expected_exit_code=1,
        )

    def test_files_command_library_count(self):
        self.run_test(
            ["files", "./robot", "--show-count", "--pythonpath", "./robot"],
            "./expected_output_count.log",
            __file__,
            expected_exit_code=1,
        )
