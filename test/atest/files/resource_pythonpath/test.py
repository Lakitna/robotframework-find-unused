from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_files_command(self):
        self.run_test(
            [
                "files",
                "./robot",
                "--pythonpath",
                "./robot/some_folder",
                "--pythonpath",
                "./robot/another_folder/something",
            ],
            "./expected_output.log",
            __file__,
            expected_exit_code=0,
        )
