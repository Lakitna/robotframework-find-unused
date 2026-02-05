import functools
from collections.abc import Generator

from robot.api import Language

from robotframework_find_unused.common.const import KeywordData, LibraryData
from robotframework_find_unused.common.normalize import normalize_keyword_name


class KeywordDefinitionManager:
    """
    Storing and finding keyword definitions.
    """

    keywords: dict[str, KeywordData]
    keywords_with_embedded_args: list[KeywordData]
    lib_keywords: dict[str, KeywordData]

    bdd_prefixes: set[str]

    def __init__(
        self,
        custom_keywords: list[KeywordData],
        downloaded_library_keywords: list[LibraryData],
    ) -> None:
        self.keywords = {}
        self.keywords_with_embedded_args = []
        for kw in custom_keywords:
            self.keywords[kw.normalized_name] = kw
            if len(kw.name_parts) > 1 and kw.name_match_pattern is not None:
                self.keywords_with_embedded_args.append(kw)

        self.lib_keywords = {}
        for lib in downloaded_library_keywords:
            for kw in lib.keywords:
                self.lib_keywords[kw.normalized_name] = kw

        # Limitation: No localisation
        language = Language.from_name("English")
        self.bdd_prefixes = {normalize_keyword_name(s) for s in language.bdd_prefixes}

    def search_keyword_definition(self, keyword_name: str) -> KeywordData | None:
        """
        Search keyword definition from keyword name or keyword call.
        """
        for normalized_name in self._keyword_name_match_options(keyword_name):
            if normalized_name in self.keywords:
                # Matched to a keyword (without embedded args)
                return self.keywords[normalized_name]

            if normalized_name in self.lib_keywords:
                # Matched to a previously unused downloaded library keyword
                return self._register_downloaded_library_keyword(normalized_name)

            keyword = self._find_keyword_with_embedded_args(normalized_name)
            if keyword is not None:
                # Matched to a keyword with embedded arguments
                return keyword

        return None

    def get_keyword_definition(self, keyword_name: str) -> KeywordData:
        """
        Get keyword definition from keyword name or keyword call.

        Always returns a definition, even if no keyword can be found.
        """
        definition = self.search_keyword_definition(keyword_name)
        if definition:
            return definition

        # Found a previously unused:
        # - non-existing keyword
        # - out-of-scope keyword
        return self._register_unknown_keyword(
            keyword_name,
            normalize_keyword_name(keyword_name),
        )

    def _keyword_name_match_options(self, name: str) -> Generator[str]:
        """
        Generate potential matchable keyword names.

        Always yields normalized names.
        """
        # Unchanged
        name_unchanged = normalize_keyword_name(name)
        yield name_unchanged

        # Without BDD prefix
        name_without_bdd = self._remove_bdd_prefix_from_name(name_unchanged)
        if name_without_bdd != name_unchanged:
            yield name_without_bdd

        # Without BDD and library prefix
        name_without_lib = self._remove_library_prefix_from_name(name_without_bdd)
        if name_without_lib != name_without_bdd:
            yield name_without_lib

    def _remove_library_prefix_from_name(self, name: str) -> str:
        """Remove Library prefix from keyword name"""
        if "." in name:
            return name.split(".", maxsplit=1)[1]
        return name

    def _remove_bdd_prefix_from_name(self, normalized_name: str) -> str:
        """Remove BDD prefix from keyword name"""
        for prefix in self.bdd_prefixes:
            if normalized_name.startswith(prefix):
                length = len(prefix)
                return normalized_name[length:].lstrip()
        return normalized_name

    def _find_keyword_with_embedded_args(self, normalized_name: str) -> KeywordData | None:
        matches = self._find_keyword_with_embedded_args_matches(normalized_name)

        if len(matches) == 0:
            return None
        if len(matches) == 1:
            return matches[0]

        def match_sorter(a: KeywordData, b: KeywordData) -> int:
            # Using same logic as in `robot/running/namespace.py`:
            # "Embedded match is considered better than another if the other matches
            # it, but it doesn't match the other."
            if self._keyword_call_matches_keyword_definition(
                a.normalized_name,
                b,
            ) and not self._keyword_call_matches_keyword_definition(
                b.normalized_name,
                a,
            ):
                return -1
            return 1

        match_order = sorted(matches, key=functools.cmp_to_key(match_sorter))
        return match_order[0]

    def _find_keyword_with_embedded_args_matches(self, normalized_name: str) -> list[KeywordData]:
        """
        Find matching keyword definitions for the keyword name.
        """
        # Fast, inconclusive pre-selection
        candidates = list(
            filter(
                lambda kw: kw.name_parts[0] == "__VARIABLE__"
                or normalized_name.startswith(kw.name_parts[0]),
                self.keywords_with_embedded_args,
            ),
        )
        if len(candidates) == 0:
            return []

        # Slow, conclusive selection
        matches: list[KeywordData] = []
        for kw in candidates:
            if self._keyword_call_matches_keyword_definition(normalized_name, kw):
                matches.append(kw)
        return matches

    def _keyword_call_matches_keyword_definition(self, call: str, definition: KeywordData) -> bool:
        if definition.name_match_pattern is None:
            msg = "Attempted to match keyword call to keyword definition without name match pattern"
            raise ValueError(msg)

        return definition.name_match_pattern.fullmatch(call) is not None

    def _register_downloaded_library_keyword(self, normalized_name: str) -> KeywordData:
        """
        Register as a downloaded library keyword.
        """
        library_keyword = self.lib_keywords[normalized_name]

        self.keywords[library_keyword.normalized_name] = library_keyword
        return self.keywords[library_keyword.normalized_name]

    def _register_unknown_keyword(self, name: str, normalized_name: str) -> KeywordData:
        """
        Register as an unknown keyword with minimum data that does not look weird.
        """
        self.keywords[normalized_name] = KeywordData(
            name=name,
            normalized_name=normalized_name,
            name_parts=[],
            name_match_pattern=None,
            argument_use_count=None,
            deprecated=None,
            private=False,
            use_count=0,
            returns=None,
            return_use_count=0,
            type="UNKNOWN",
            arguments=None,
            library="",
        )
        return self.keywords[normalized_name]
