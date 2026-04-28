from dataclasses import dataclass

from robotframework_find_unused.common.const import FilterOption


@dataclass
class ArgumentsOptions:
    """
    Command line options for the 'arguments' command
    """

    deprecated_keywords: FilterOption
    private_keywords: FilterOption
    library_keywords: FilterOption
    unused_keywords: FilterOption
    keyword_filter_glob: str | None
    show_all_count: bool
    verbose: int
    source_path: str
