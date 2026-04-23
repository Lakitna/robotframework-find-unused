from pathlib import Path


class PartialBaseReporterDiscoverFiles:
    """
    Partial base reporter for discovering files.
    """

    def on_discover_files_start(self, root_folder: str):
        """Before files to be analyzed are discovered"""

    def on_discover_files_success(self, root_folder: str, discovered_files: list[Path]):
        """When discovering files was a success"""

    def on_discover_files_fail(self, root_folder: str, errors: list[str]):
        """When discovering files fails"""
