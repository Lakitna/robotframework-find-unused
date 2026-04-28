from dataclasses import dataclass

from robotframework_find_unused.common.const import FilterOption


@dataclass
class FileOptions:
    """
    Command line options for the 'files' command
    """

    show_all_count: bool
    library_files: FilterOption
    variable_files: FilterOption
    resource_files: FilterOption
    unused_files: FilterOption
    path_filter_glob: str | None
    show_tree: bool
    tree_max_depth: int
    tree_max_height: int
    verbose: int
    source_path: str
    pythonpath: list[str]
