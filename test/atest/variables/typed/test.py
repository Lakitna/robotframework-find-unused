from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_variables_command_typed_variables(self):
        self.run_test(
            ["variables", "./robot"],
            "./expected_output.log",
            __file__,
            expected_exit_code=7,
            # Typed variables where introduced in 7.3.0
            min_robot_version="7.3.0",
        )

    def test_variables_command_typed_variables_show_count(self):
        self.run_test(
            ["variables", "./robot", "--show-count"],
            "./expected_output_count.log",
            __file__,
            expected_exit_code=7,
            # Typed variables where introduced in 7.3.0
            min_robot_version="7.3.0",
        )
