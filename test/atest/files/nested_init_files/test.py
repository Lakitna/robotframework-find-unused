from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_files_command_tree_nested_init_files(self):
        self.run_test(
            ["files", "./robot", "--show-tree"],
            "./expected_output_tree.log",
            __file__,
            expected_exit_code=0,
        )
