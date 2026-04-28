import os
import sys
from pathlib import Path

import click

from robotframework_find_unused.common.const import (
    VERBOSE_DOUBLE,
    VERBOSE_NO,
    VERBOSE_SINGLE,
)
from robotframework_find_unused.reporter.base.partial.discover_files import (
    PartialReporter_DiscoverFiles,
)
from robotframework_find_unused.reporter.cli.common import (
    DONE,
    ERROR,
    INDENT,
    NOTE,
)


class PartialCliReporterDiscoverFiles(PartialReporter_DiscoverFiles):
    """
    Partial CLI reporter for discovering files.
    """

    def on_discover_files_start(self, root_folder: str):
        """Before files to be analyzed are discovered"""
        click.echo(f"Discovering files in `{root_folder}` using Robocop config...")

    def on_discover_files_fail(self, root_folder: str, errors: list[str]):
        """When discovering files fails"""
        for err in errors:
            click.echo(f"{ERROR} {err}")

        click.echo(f"{NOTE} All files in Robocop config `exclude` are ignored")
        click.echo(f"{NOTE} All files listed in `.gitignore` files are ignored")

        if self.options.verbose < VERBOSE_DOUBLE:
            click.echo(
                f"{NOTE} Run with `--verbose --verbose` or `-vv` for more details",
            )
            sys.exit(255)
            return

        click.echo(f"{NOTE} All of the following files are excluded:")
        for root, _dirs, files in os.walk(root_folder):
            for file in files:
                click.echo(f"{INDENT}{Path(root, file).as_posix()}")

        sys.exit(255)

    def on_discover_files_success(
        self,
        root_folder: str,
        discovered_files: list[Path],
    ):
        """When discovering files was a success"""
        if self.options.verbose == VERBOSE_NO:
            return

        click.echo(f"{DONE} Discovered {len(discovered_files)} files")

        if self.options.verbose == VERBOSE_SINGLE:
            return

        for path in discovered_files:
            click.echo(INDENT + click.style(str(path), fg="bright_black"))
