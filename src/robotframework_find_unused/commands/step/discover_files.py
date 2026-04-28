from pathlib import Path

import robocop

from robotframework_find_unused.reporter.base.partial.discover_files import (
    PartialReporter_DiscoverFiles,
)

FILE_EXTENSIONS = {"*.robot", "*.resource", "*.py"}


def step_discover_file_paths(
    input_path: str,
    *,
    reporter: PartialReporter_DiscoverFiles,
) -> list[Path] | None:
    """
    Get file paths recursively with Robocop excludes.
    """
    reporter.on_discover_files_start(input_path)

    if robocop.__version__.startswith("6.") or robocop.__version__.startswith("7."):
        file_paths = _discover_file_paths_robocop_6_7(input_path)
    else:
        file_paths = _discover_file_paths_robocop(input_path)

    sorted_file_paths = sorted(file_paths, key=lambda f: f)
    sorted_file_paths = sorted(
        sorted_file_paths,
        key=lambda p: len(p.parts)
        # __init__ files should always be before the files they apply to
        + (-0.5 if p.stem == "__init__" else 0),
    )

    if len(sorted_file_paths) == 0:
        reporter.on_discover_files_fail(
            input_path,
            [f"Found 0 files in `{input_path}`"],
        )
        return None

    reporter.on_discover_files_success(input_path, sorted_file_paths)
    return sorted_file_paths


def _discover_file_paths_robocop_6_7(input_path: str) -> list[Path]:
    """
    Get file paths recursively with Robocop.

    Only works for Robocop 6.x.x and 7.x.x
    """
    from robocop.config import ConfigManager, FileFiltersOptions  # type: ignore  # noqa: PGH003

    robocop_config = ConfigManager(sources=[input_path])

    extensions = FILE_EXTENSIONS
    if robocop_config.default_config.file_filters:
        robocop_config.default_config.file_filters.default_include = extensions
    else:
        robocop_config.default_config.file_filters = FileFiltersOptions(default_include=extensions)

    return [path[0] for path in robocop_config.paths]


def _discover_file_paths_robocop(input_path: str) -> list[Path]:
    """
    Get file paths recursively with Robocop.

    Works for Robocop 8.x.x and up
    """
    from robocop.config.builder import (
        RawConfig,  # type: ignore  # noqa: PGH003
        RawFileFiltersOptions,  # type: ignore  # noqa: PGH003
    )
    from robocop.config.manager import ConfigManager  # type: ignore  # noqa: PGH003

    config_manager = ConfigManager(
        sources=[input_path],
        overwrite_config=RawConfig(
            file_filters=RawFileFiltersOptions(default_include=list(FILE_EXTENSIONS)),
        ),
    )

    return [source_file.path for source_file in config_manager.paths]
