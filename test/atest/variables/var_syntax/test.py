from test.atest.utils import AcceptanceTest


class TestCommandAcceptance(AcceptanceTest):
    def test_variables_command_with_count(self):
        self.run_test(
            ["variables", "./robot", "--show-count"],
            "./expected_output_count.log",
            __file__,
            expected_exit_code=6,
            # VAR syntax was introduced in 7.0.0
            min_robot_version="7.0.0",
        )
