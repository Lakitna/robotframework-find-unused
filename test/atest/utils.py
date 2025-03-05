import difflib
import subprocess
import sys
from pathlib import Path

import click
import pytest


class AcceptanceTest:
    def test(self, cli_options: list[str], expected_output_path: str, test_file_path: str):
        test_folder = Path(test_file_path).parent
        expected_output_path: Path = test_folder.joinpath(expected_output_path)

        with expected_output_path.open() as f:
            expected_output = f.read()

        command = [sys.executable, "-m", "robotframework_find_unused"]
        command.extend(cli_options)

        p = subprocess.run(  # noqa: S603
            command,
            capture_output=True,
            cwd=test_folder,
            check=True,
        )

        actual = p.stdout.decode()
        expected = expected_output

        self._assert_logs(actual, expected)

    def _assert_logs(self, actual: str, expected: str) -> None:
        actual_lines = actual.splitlines()
        expected_lines = expected.splitlines()
        diff = difflib.ndiff(actual_lines, expected_lines)

        error = ["Actual output does not match expected output. Diff:"]
        for diff_line in diff:
            if diff_line.startswith("- "):
                error.append(click.style(diff_line, fg="red"))
            elif diff_line.startswith("+ "):
                error.append(click.style(diff_line, fg="green"))
            else:
                error.append(diff_line)

        pytest.fail("\n".join(error), pytrace=False)
