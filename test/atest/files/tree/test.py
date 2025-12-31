from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_files_command_tree(self):
        self.run_test(
            ["files", "./robot", "--show-tree"],
            "./expected_output_tree.log",
            __file__,
            expected_exit_code=0,
        )

    def test_files_command_max_depth(self):
        self.run_test(
            ["files", "./robot", "--show-tree", "--tree-max-depth", "2"],
            "./expected_output_max_depth.log",
            __file__,
            expected_exit_code=0,
        )

    def test_files_command_max_height(self):
        self.run_test(
            ["files", "./robot", "--show-tree", "--tree-max-height", "3"],
            "./expected_output_max_height.log",
            __file__,
            expected_exit_code=0,
        )
