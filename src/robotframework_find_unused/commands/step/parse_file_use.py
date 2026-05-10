from pathlib import Path

from robotframework_find_unused.common.const import FileUseData, FileUsedByData, ResolvedFileImport
from robotframework_find_unused.common.normalize import normalize_file_path
from robotframework_find_unused.reporter.base.file_reporter import FileReporter
from robotframework_find_unused.visitors.robot import visit_robot_files
from robotframework_find_unused.visitors.robot.file_import import RobotVisitorFileImports


def step_parse_file_use(file_paths: list[Path], source_path: Path, *, reporter: FileReporter):
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
    Walk through all robot files to keep track of imports. Only returns user files.
    """
    visitor = RobotVisitorFileImports(source_path, set(file_paths), reporter)
    visit_robot_files(
        file_paths,
        visitor,
        parse_sections=("settings", "keywords", "test cases", "tasks"),
    )
    files_dict = _add_undiscovered_files(file_paths, visitor.files)

    files_list = list(files_dict.values())

    _raise_import_warnings(files_list, reporter)

    # Remove downloaded library and builtin files. We no longer need them.
    return [f for f in files_list if f.resolved_to.type not in ("BUILTIN", "DOWNLOADED_LIBRARY")]


def _add_undiscovered_files(
    file_paths: list[Path],
    files: dict[str, FileUseData],
) -> dict[str, FileUseData]:
    for path in file_paths:
        path_normalized = normalize_file_path(path)
        if path_normalized in files:
            continue

        files[path_normalized] = FileUseData(
            id=path_normalized,
            resolved_to=ResolvedFileImport(
                type="FILE_PATH",
                import_string=path.as_posix(),
                path=path,
            ),
            type=set(),
            used_by=[],
        )

    return files


def _raise_import_warnings(files: list[FileUseData], reporter: FileReporter) -> None:
    for file in files:
        used_by_grouped_by_alias: dict[str | None, list[FileUsedByData]] = {}
        for used_by in file.used_by:
            if used_by.normalized_as_alias not in used_by_grouped_by_alias:
                used_by_grouped_by_alias[used_by.normalized_as_alias] = []

            used_by_grouped_by_alias[used_by.normalized_as_alias].append(used_by)

        distinct_args = set()
        for used_by_group in used_by_grouped_by_alias.values():
            for f in used_by_group:
                distinct_args.add(f.args)

        if len(distinct_args) > 1:
            reporter.on_file_imports_with_different_args(file)
