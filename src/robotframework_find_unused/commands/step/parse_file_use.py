from pathlib import Path

from robotframework_find_unused.common.const import FileUseData
from robotframework_find_unused.common.normalize import normalize_file_path
from robotframework_find_unused.reporter.base.file_reporter import FileReporter
from robotframework_find_unused.visitors.robot import visit_robot_files
from robotframework_find_unused.visitors.robot.file_import import RobotVisitorFileImports


def step_step_parse_file_use(file_paths: list[Path], source_path: Path, *, reporter: FileReporter):
    """
    Parse files and keep the user up-to-date on progress
    """
    reporter.on_count_file_uses_start(file_paths, source_path)

    files = _count_file_uses(file_paths, source_path, reporter)

    reporter.on_count_file_uses_end(file_paths, source_path, files)
    return files


def _count_file_uses(
    file_paths: list[Path],
    source_path: Path,
    reporter: FileReporter,
) -> list[FileUseData]:
    """
    Walk through all robot files to keep track of imports.
    """
    visitor = RobotVisitorFileImports(source_path, set(file_paths), reporter)
    visit_robot_files(
        file_paths,
        visitor,
        parse_sections=("settings", "keywords", "test cases", "tasks"),
    )
    files = visitor.files

    # Add undiscovered files from input file paths
    for path in file_paths:
        path_normalized = normalize_file_path(path)
        if path_normalized in files:
            continue

        files[path_normalized] = FileUseData(
            id=path_normalized,
            path_absolute=path,
            type=set(),
            used_by=[],
        )

    return list(files.values())
