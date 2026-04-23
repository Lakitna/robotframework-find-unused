from dataclasses import dataclass

from robotframework_find_unused.common.const import FilterOption


@dataclass
class KeywordOptions:
    """
    Command line options for the 'keywords' command
    """

    show_all_count: bool
    deprecated_keywords: FilterOption
    private_keywords: FilterOption
    library_keywords: FilterOption
    unused_library_keywords: FilterOption
    keyword_filter_glob: str | None
    verbose: int
    source_path: str
