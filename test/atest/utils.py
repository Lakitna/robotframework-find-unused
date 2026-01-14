import difflib
import os
import re
import subprocess
import sys
from pathlib import Path

import click
import pytest
import robot
from packaging.version import Version


class AcceptanceTest:
    def run_test(
        self,
        cli_options: list[str],
        expected_output_path: str,
        test_file_path: str,
        expected_exit_code: int = 0,
        min_robot_version: str | None = None,
    ):
        if self._skip_for_robot_version(min_robot_version):
            pytest.skip("Skipped due to Robot version")

        test_folder = Path(test_file_path).parent
        test_data_folder = test_folder.joinpath(cli_options[1])
        sys.path.append(str(test_data_folder))

        expected_output_path_absolute: Path = test_folder.joinpath(expected_output_path)
        with expected_output_path_absolute.open(encoding="utf8") as f:
            expected_output = f.read()

        command = [sys.executable, "-m", "robotframework_find_unused"]
        command.extend(cli_options)

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf8"
        p = subprocess.run(  # noqa: S603
            command,
            cwd=test_folder,
            check=False,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding="utf8",
        )

        actual_output = self._parse_output(p.stdout)
        self._assert_logs(actual_output, expected_output)

        if p.returncode != expected_exit_code:
            pytest.fail(
                (
                    f"Subprocess exited with unexpected exit code {p.returncode}. "
                    f"Expected exit code: {expected_exit_code} "
                    f"Actual exit code: {p.returncode} "
                    f"Subprocess stdout below:\n{p.stdout}\n"
                ),
            )

    def _skip_for_robot_version(self, min_version: str | None) -> bool:
        if min_version is None:
            return False

        min_v = Version(min_version)
        robot_v = Version(robot.get_version())
        return robot_v < min_v

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

        # Remove file path to the repository root
        repo_root = get_repo_root(Path(__file__))
        output = output.replace(repo_root.as_posix(), "[[REPOSITORY_ROOT]]")

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


def get_repo_root(file_path: Path) -> Path:
    """Find repository root from the path's parents"""
    for path in file_path.parents:
        # Check whether "path/.git" exists and is a directory
        if path.joinpath(".git").is_dir():
            return path

    msg = (
        "Failed to find repository root. "
        f"No parent of `{file_path.as_posix()}` contains a `.git` folder."
    )
    raise FileNotFoundError(msg)
