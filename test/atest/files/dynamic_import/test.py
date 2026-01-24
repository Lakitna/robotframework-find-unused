from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_files_command_dynamic_import(self):
        self.run_test(
            ["files", "./robot", "--show-tree"],
            "./expected_output_tree.log",
            __file__,
            expected_exit_code=1,
        )
