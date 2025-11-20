from .const import KeywordData


def sort_keywords_by_name(unsorted: list[KeywordData]) -> list[KeywordData]:
    """Sort list of keyword by library name and keyword name"""
    return sorted(unsorted, key=lambda kw: f"{kw.library or 'aaa'}.{kw.normalized_name}")
