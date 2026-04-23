"""
Implementation of the 'keywords' command
"""

from robotframework_find_unused.commands.step.discover_files import cli_discover_file_paths
from robotframework_find_unused.commands.step.keyword_count_uses import cli_count_keyword_uses
from robotframework_find_unused.commands.step.keyword_definitions import (
    cli_step_get_custom_keyword_definitions,
)
from robotframework_find_unused.commands.step.lib_keyword_definitions import (
    cli_step_get_downloaded_lib_keywords,
)
from robotframework_find_unused.commands.step.parse_files import cli_step_parse_files_with_libdoc
from robotframework_find_unused.reporter.base.keyword_reporter import KeywordReporter

from .options import KeywordOptions


def cli_keywords(options: KeywordOptions, reporter: KeywordReporter) -> None:
    """
    Entry point for the CLI command
    """
    reporter.on_command_start()

    file_paths = cli_discover_file_paths(options.source_path, reporter=reporter)
    if file_paths is None:
        return

    files = cli_step_parse_files_with_libdoc(file_paths, reporter=reporter)

    keywords = cli_step_get_custom_keyword_definitions(files, reporter=reporter)
    if len(keywords) == 0 and options.library_keywords == "exclude":
        return

    downloaded_library_keywords = cli_step_get_downloaded_lib_keywords(
        file_paths,
        reporter=reporter,
    )

    counted_keywords = cli_count_keyword_uses(
        file_paths,
        keywords,
        downloaded_library_keywords,
        reporter=reporter,
    )

    reporter.on_command_end(counted_keywords)
