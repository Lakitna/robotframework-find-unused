import difflib
import re
import subprocess
import sys
from pathlib import Path

import click
import pytest


class AcceptanceTest:
    def run_test(
        self,
        cli_options: list[str],
        expected_output_path: str,
        test_file_path: str,
        expected_exit_code: int = 0,
    ):
        test_folder = Path(test_file_path).parent
        expected_output_path_absolute: Path = test_folder.joinpath(expected_output_path)

        with expected_output_path_absolute.open() as f:
            expected_output = f.read()

        command = [sys.executable, "-m", "robotframework_find_unused"]
        command.extend(cli_options)

        p = subprocess.run(  # noqa: S603
            command,
            capture_output=True,
            cwd=test_folder,
            check=False,
        )

        actual_output = self._parse_output(p.stdout.decode())
        self._assert_logs(actual_output, expected_output)

        if p.returncode != expected_exit_code:
            pytest.fail(
                (
                    f"Subprocess exited with unexpected exit code {p.returncode}. "
                    f"Expected exit code: {expected_exit_code} "
                    f"Actual exit code: {p.returncode} "
                    f"Subprocess stderr below:\n{p.stderr.decode()}\n"
                    f"Subprocess stdout below:\n{p.stdout.decode()}\n"
                ),
            )

    def _assert_logs(self, actual: str, expected: str) -> None:
        actual_lines = actual.splitlines()
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

    def _parse_output(self, output: str) -> str:
        output = output.strip()

        # Remove the keyword use count from standard libraries
        builtin_libraries = [
            "BuiltIn",
            "Collections",
            "DateTime",
            "OperatingSystem",
            "Process",
            "String",
            "XML",
        ]
        for lib in builtin_libraries:
            output = re.sub(f"(    {lib}: )\\d+", r"\1[[MASK]]", output)

        return output
