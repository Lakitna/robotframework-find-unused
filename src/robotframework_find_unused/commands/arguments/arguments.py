"""
Implementation of the 'arguments' command
"""

from typing import TYPE_CHECKING

from robotframework_find_unused.commands.step.discover_files import step_discover_file_paths
from robotframework_find_unused.commands.step.keyword_count_uses import step_count_keyword_uses
from robotframework_find_unused.commands.step.keyword_definitions import (
    step_step_get_custom_keyword_definitions,
)
from robotframework_find_unused.commands.step.keyword_filter import cli_filter_keywords
from robotframework_find_unused.commands.step.lib_keyword_definitions import (
    step_step_get_downloaded_lib_keywords,
)
from robotframework_find_unused.commands.step.parse_files import step_step_parse_files_with_libdoc

if TYPE_CHECKING:
    from robotframework_find_unused.reporter.base.argument_reporter import ArgumentReporter

    from .options import ArgumentsOptions


def command_arguments(options: "ArgumentsOptions", reporter: "ArgumentReporter") -> None:
    """
    Entry point for the CLI command 'arguments'
    """
    reporter.on_command_start()

    file_paths = step_discover_file_paths(options.source_path, reporter=reporter)
    if file_paths is None:
        return

    files = step_step_parse_files_with_libdoc(file_paths, reporter=reporter)

    keywords = step_step_get_custom_keyword_definitions(files, reporter=reporter)
    if len(keywords) == 0 and options.library_keywords == "exclude":
        return

    downloaded_library_keywords = step_step_get_downloaded_lib_keywords(
        file_paths,
        reporter=reporter,
    )

    counted_keywords = step_count_keyword_uses(
        file_paths,
        keywords,
        downloaded_library_keywords,
        reporter=reporter,
    )

    if options.library_keywords != "exclude" and options.unused_keywords != "exclude":
        for lib in downloaded_library_keywords:
            for kw in lib.keywords:
                if kw in counted_keywords:
                    continue
                counted_keywords.append(kw)

    counted_keywords = cli_filter_keywords(
        counted_keywords,
        filter_deprecated=options.deprecated_keywords,
        filter_private=options.private_keywords,
        filter_library=options.library_keywords,
        filter_unused=options.unused_keywords,
        filter_glob=options.keyword_filter_glob,
    )

    reporter.on_command_end(counted_keywords)
