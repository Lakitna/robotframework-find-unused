import difflib
import subprocess
import sys
from pathlib import Path

import click
import pytest


class AcceptanceTest:
    def run_test(self, cli_options: list[str], expected_output_path: str, test_file_path: str):
        test_folder = Path(test_file_path).parent
        expected_output_path_absolute: Path = test_folder.joinpath(expected_output_path)

        with expected_output_path_absolute.open() as f:
            expected_output = f.read()

        command = [sys.executable, "-m", "robotframework_find_unused"]
        command.extend(cli_options)

        try:
            p = subprocess.run(  # noqa: S603
                command,
                capture_output=True,
                cwd=test_folder,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            pytest.fail(
                f"Subprocess failed with non-zero exit code {e.returncode}. "
                "Subprocess stderr below:\n" + e.stderr.decode(),
            )

        actual = p.stdout.decode()
        expected = expected_output

        self._assert_logs(actual, expected)

    def _assert_logs(self, actual: str, expected: str) -> None:
        actual_lines = actual.strip().splitlines()
        expected_lines = expected.strip().splitlines()
        diff = difflib.ndiff(actual_lines, expected_lines)

        error_msg = ["Actual output does not match expected output. Diff:"]
        error = False
        for diff_line in diff:
            if diff_line.startswith("- "):
                error_msg.append(click.style(diff_line, fg="red"))
                error = True
            elif diff_line.startswith("+ "):
                error_msg.append(click.style(diff_line, fg="green"))
                error = True
            else:
                error_msg.append(diff_line)

        if error:
            pytest.fail("\n".join(error_msg), pytrace=False)
