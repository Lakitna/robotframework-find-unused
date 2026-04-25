from pathlib import Path

import click

from robotframework_find_unused.common.const import (
    DONE_MARKER,
    INDENT,
    VERBOSE_NO,
    WARN_MARKER,
    KeywordData,
)
from robotframework_find_unused.reporter.base.partial.count_keywords import (
    PartialReporter_CountKeywords,
)
from robotframework_find_unused.visitors.robot.library_import import LibraryData


class PartialCliReporterCountKeywords(PartialReporter_CountKeywords):
    """
    Partial CLI reporter for counting keywords.
    """

    def on_count_keyword_uses_start(
        self,
        file_paths: list[Path],
        keywords: list[KeywordData],
        downloaded_libraries: list[LibraryData],
    ):
        click.echo("Counting keyword usage...")

    def on_count_keyword_uses_end(
        self,
        file_paths: list[Path],
        keywords: list[KeywordData],
        downloaded_libraries: list[LibraryData],
        counted_keywords: list[KeywordData],
    ):
        total_uses = sum([kw.use_count for kw in counted_keywords])
        click.echo(
            (WARN_MARKER if total_uses == 0 else DONE_MARKER)
            + f" Processed {total_uses} keyword calls",
        )

        if self.options.verbose > VERBOSE_NO:
            kw_type_use_count: dict[str, int] = {}
            for kw in counted_keywords:
                if kw.type not in kw_type_use_count:
                    kw_type_use_count[kw.type] = 0
                kw_type_use_count[kw.type] += kw.use_count

            for kw_type, count in sorted(
                kw_type_use_count.items(),
                key=lambda x: x[1],
                reverse=True,
            ):
                click.echo(f"{INDENT}{count} calls to keywords of type {kw_type}")

            click.echo(
                (WARN_MARKER if len(counted_keywords) == 0 else DONE_MARKER)
                + f" Found {len(counted_keywords)} unique keywords "
                + click.style("(keyword definitions and calls)", fg="bright_black"),
            )

        unknown_keywords = [kw for kw in counted_keywords if kw.type == "UNKNOWN"]
        if len(unknown_keywords) > 0:
            click.echo(
                f"{WARN_MARKER} Found {len(unknown_keywords)} called keywords without a definition",
            )

        if self.options.verbose > VERBOSE_NO:
            for kw in unknown_keywords:
                click.echo(f"{INDENT}{kw.name}")
