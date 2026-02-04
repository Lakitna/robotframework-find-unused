import functools
from collections.abc import Generator, Iterable
from dataclasses import dataclass
from typing import Any, Literal

from robot.api import Language
from robot.api.parsing import (
    File,
    Keyword,
    KeywordCall,
    ModelVisitor,
    Setup,
    SuiteSetup,
    SuiteTeardown,
    Teardown,
    Template,
    TemplateArguments,
    TestCase,
    TestSetup,
    TestTeardown,
    TestTemplate,
    Token,
)
from robot.libdocpkg.model import ArgumentSpec
from robot.parsing.model.blocks import Block
from robot.running.arguments.argumentmapper import DefaultValue

from robotframework_find_unused.common.const import KeywordData
from robotframework_find_unused.common.normalize import normalize_keyword_name
from robotframework_find_unused.visitors.robot.library_import import LibraryData


@dataclass
class KeywordCallData:
    """
    Simplified keyword call data structure
    """

    keyword: str
    args: tuple[str, ...]


class RobotVisitorKeywords(ModelVisitor):
    """
    A Robot Framework visitor.

    Gathers keywords
    Counts keyword usage
    Counts keyword argument usage
    Counts keyword return usage
    """

    keywords: dict[str, KeywordData]
    keywords_with_embedded_args: list[KeywordData]
    downloaded_libraries: list[LibraryData]
    normalized_keyword_names: set[str]
    suite_template_keyword: str | None

    bdd_prefixes: set[str]

    def __init__(
        self,
        custom_keywords: list[KeywordData],
        downloaded_library_keywords: list[LibraryData],
    ) -> None:
        self.normalized_keyword_names = set()
        self.keywords = {}
        self.keywords_with_embedded_args = []
        self.suite_template_keyword = None

        for kw in custom_keywords:
            self.keywords[kw.normalized_name] = kw
            self.normalized_keyword_names.add(kw.normalized_name)
            if len(kw.name_parts) > 1 and kw.name_match_pattern is not None:
                self.keywords_with_embedded_args.append(kw)

        self.downloaded_libraries = downloaded_library_keywords
        for lib in self.downloaded_libraries:
            self.normalized_keyword_names.update(lib.keyword_names_normalized)

        # Limitation: No localisation
        language = Language.from_name("English")
        self.bdd_prefixes = {normalize_keyword_name(s) for s in language.bdd_prefixes}

    def visit_File(self, node: File):  # noqa: N802
        """Visit new file"""
        self.suite_template_keyword = None

        return self.generic_visit(node)

    def visit_Keyword(self, node: Keyword):  # noqa: N802
        """Keyword definition"""
        keyword = self._get_keyword_data(node.name)
        keyword.returns = self._get_keyword_returns(node)

        return self.generic_visit(node)

    def visit_KeywordCall(self, node: KeywordCall):  # noqa: N802
        """Keyword call / Keyword use"""
        return_assign_token = node.get_token(Token.ASSIGN)

        self._count_keyword_call(
            node.keyword,
            node.args,
            return_value_assigned=(return_assign_token is not None),
        )

        return self.generic_visit(node)

    def visit_Setup(self, node: Setup):  # noqa: N802
        """Count keyword use in test/task/keyword setup"""
        keyword_name_token = node.get_token(Token.NAME)
        if keyword_name_token:
            self._count_keyword_call(str(keyword_name_token), args=[])

        return self.generic_visit(node)

    def visit_Teardown(self, node: Teardown):  # noqa: N802
        """Count keyword use in test/task/keyword teardown"""
        keyword_name_token = node.get_token(Token.NAME)
        if keyword_name_token:
            self._count_keyword_call(str(keyword_name_token), args=[])

        return self.generic_visit(node)

    def visit_TestSetup(self, node: TestSetup):  # noqa: N802
        """Count keyword use in test setup"""
        self._count_keyword_call(node.name, node.args)

        return self.generic_visit(node)

    def visit_SuiteSetup(self, node: SuiteSetup):  # noqa: N802
        """Count keyword use in suite setup"""
        self._count_keyword_call(node.name, node.args)

        return self.generic_visit(node)

    def visit_TestTeardown(self, node: TestTeardown):  # noqa: N802
        """Count keyword use in test teardown"""
        self._count_keyword_call(node.name, node.args)

        return self.generic_visit(node)

    def visit_SuiteTeardown(self, node: SuiteTeardown):  # noqa: N802
        """Count keyword use in suite teardown"""
        self._count_keyword_call(node.name, node.args)

        return self.generic_visit(node)

    def visit_TestTemplate(self, node: TestTemplate):  # noqa: N802
        """Count keyword use in test template setting"""
        if not node.value:
            return self.generic_visit(node)

        self.suite_template_keyword = node.value
        self._count_keyword_call(
            self.suite_template_keyword,
            # Arguments are not allowed here
            args=(),
            count_arguments=False,
        )
        return self.generic_visit(node)

    def visit_TestCase(self, node: TestCase):  # noqa: N802
        """Count templated test cases"""
        test_template_keyword = None
        template_args_set = []
        for child in node.body:
            if isinstance(child, Template):
                test_template_keyword = str(child.get_token(Token.NAME))
                continue
            if isinstance(child, TemplateArguments):
                args = child.get_tokens(Token.ARGUMENT)
                args = [str(arg) for arg in args]
                template_args_set.append(args)
                continue

        if test_template_keyword is not None:
            # There is a [Template] defined on the test
            self._count_keyword_call(
                test_template_keyword,
                # Arguments are not allowed here
                (),
                count_arguments=False,
            )
            for args in template_args_set:
                self._count_keyword_call(test_template_keyword, args, count_keyword=False)
        elif self.suite_template_keyword is not None:
            # There is a Template defined in *** settings ***
            for args in template_args_set:
                self._count_keyword_call(self.suite_template_keyword, args, count_keyword=False)

        return self.generic_visit(node)

    def _remove_lib_from_name(self, name: str) -> str:
        """Remove Library prefix from keyword name"""
        if "." in name:
            return name.split(".", maxsplit=1)[1]
        return name

    def _remove_bdd_prefix_from_name(self, name: str, normalized_name: str) -> str:
        """Remove BDD prefix from keyword name"""
        for prefix in self.bdd_prefixes:
            if normalized_name.startswith(prefix):
                length = len(prefix)
                return name[length:].lstrip()
        return name

    def _get_keyword_match_options(self, name: str) -> Generator[tuple[str, str]]:
        # Unchanged
        name_unchanged = name
        normalized_name_unchanged = normalize_keyword_name(name)
        yield (name, normalized_name_unchanged)

        # Without BDD prefix
        name_without_bdd = self._remove_bdd_prefix_from_name(
            name_unchanged,
            normalized_name_unchanged,
        )
        if name_without_bdd != name_unchanged:
            yield (
                name_without_bdd,
                normalize_keyword_name(name_without_bdd),
            )

        # Without BDD and library prefix
        name_without_lib = self._remove_lib_from_name(name_without_bdd)
        if name_without_lib != name_without_bdd:
            yield (
                name_without_lib,
                normalize_keyword_name(name_without_lib),
            )

    def _get_keyword_data(self, keyword_name: str) -> KeywordData:
        for name, normalized_name in self._get_keyword_match_options(keyword_name):
            if normalized_name in self.keywords:
                # Matched to a keyword (without embedded args)
                return self.keywords[normalized_name]

            if normalized_name in self.normalized_keyword_names:
                # Matched to a previously unused downloaded library keyword
                return self._register_downloaded_library_keyword(name, normalized_name)

            keyword = self._find_keyword_with_embedded_args(normalized_name)
            if keyword is not None:
                # Matched to a keyword with embedded arguments
                return keyword

        # Found a previously unused:
        # - non-existing keyword
        # - out-of-scope keyword
        return self._register_unknown_keyword(keyword_name, normalize_keyword_name(keyword_name))

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

    def _count_keyword_call(
        self,
        name: str,
        args: Iterable[str],
        *,
        return_value_assigned: bool = False,
        count_keyword: bool = True,
        count_arguments: bool = True,
    ) -> None:
        """
        Count the keyword.

        For keywords that take other keywords as arguments: Recursively handle inner keyword.
        """
        keyword = self._get_keyword_data(name)
        if count_keyword:
            keyword.use_count += 1

        if return_value_assigned:
            keyword.return_use_count += 1

        inner_keywords = self._get_keyword_reference_in_argument(args, keyword)
        for inner in inner_keywords:
            self._count_keyword_call(inner.keyword, inner.args)

        if count_arguments:
            self._count_keyword_call_args(keyword, args)

    def _get_keyword_reference_in_argument(
        self,
        args: Iterable[str],
        keyword: KeywordData,
    ) -> list[KeywordCallData]:
        """
        Return keyword calls in the given arguments

        - Only considers known keywords
        - Only considers cases where the keyword name or argument name includes 'keyword'

        Returns a list of tuples where (inner_keywor_name, inner_keyword_arguments)
        """
        inner_keywords: list[KeywordCallData] = []

        args = tuple(a for a in args)
        for i, arg in enumerate(args):
            arg_value = self._argument_is_keyword_reference(arg, i, keyword)
            if arg_value is False:
                continue

            inner_keywords.append(KeywordCallData(keyword=arg_value, args=args[i + 1 :]))

        if len(inner_keywords) > 1:
            for i in range(1, len(inner_keywords)):
                cur = inner_keywords[i]
                prev = inner_keywords[i - 1]

                prev.args = self._get_deduped_arguments(
                    prev,
                    cur,
                )

        return inner_keywords

    def _argument_is_keyword_reference(
        self,
        arg: str,
        position_index: int,
        keyword: KeywordData,
    ) -> Literal[False] | str:
        arg_name = None
        arg_val = arg
        if "=" in arg:
            # Is a named arg
            (arg_name, arg_val) = arg.split("=", 1)

        if "." in arg_val:
            # Remove library prefix
            arg_val = arg_val.split(".", 1)[1]

        normalized_name = normalize_keyword_name(arg_val)
        if normalized_name not in self.normalized_keyword_names:
            # Not a known keyword name
            return False

        # Limitation: No localisation
        if "keyword" in keyword.normalized_name:
            return arg_val

        if arg_name is None:
            # Argument is positional. Named arg can't get here.
            arg_name = self._get_keyword_arg_name_by_position_index(
                keyword,
                position_index=position_index,
            )
        if arg_name is None:
            return False

        arg_name = arg_name.lower()
        # Limitation: No localisation
        if "keyword" in arg_name:
            return arg_val

        return False

    def _get_keyword_arg_name_by_position_index(
        self,
        keyword: KeywordData,
        position_index: int,
    ) -> str | None:
        """
        Return the argument name at the given positional index.

        Does not consider named arguments.
        """
        if keyword.arguments is None:
            # We don't know anything about the defined keyword arguments
            return None

        if keyword.arguments.var_positional and position_index > len(
            keyword.arguments.positional,
        ):
            # @{varargs} used
            return keyword.arguments.var_positional

        if position_index < len(keyword.arguments.argument_names):
            return keyword.arguments.argument_names[position_index]

        return None

    def _get_deduped_arguments(
        self,
        call: KeywordCallData,
        duplicate_call: KeywordCallData,
    ) -> tuple[str, ...]:
        """
        Deduplicate arguments of the first keyword call.

        Used to prevent counting a keyword multiple times.
        """
        args_to_remove = (duplicate_call.keyword, *duplicate_call.args)

        output = [*call.args]
        for i in range(len(args_to_remove)):
            remove_val = args_to_remove[-i - 1]
            if "=" in remove_val:
                (_, remove_val) = remove_val.split("=", 1)

            actual_val = output.pop()
            if "=" in actual_val:
                (_, actual_val) = actual_val.split("=", 1)

            if remove_val == actual_val:
                continue
            if "." in remove_val and remove_val.endswith("." + actual_val):
                continue
            if "." in actual_val and actual_val.endswith("." + remove_val):
                continue

            msg = f"Expected list to end with '{remove_val}', but found '{actual_val}' instead"
            raise ValueError(msg)

        return tuple(output)

    def _register_downloaded_library_keyword(self, name: str, normalized_name: str) -> KeywordData:
        """
        Register as a downloaded library keyword.
        """
        library = None
        for lib in self.downloaded_libraries:
            if normalized_name in lib.keyword_names_normalized:
                library = lib
                break

        if library is None:
            msg = f"Can't find library for keyword '{name}'"
            raise Exception(msg)  # noqa: TRY002

        library_keyword = None
        for kw in library.keywords:
            if kw.normalized_name == normalized_name:
                library_keyword = kw
                break

        if library_keyword is None:
            msg = f"Can't find keyword '{name}' in library '{library.name}'"
            raise Exception(msg)  # noqa: TRY002

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

    def _parse_args(
        self,
        call_args: Iterable[str],
        kw_args: ArgumentSpec,
    ) -> tuple[list[str], list[tuple[str, Any]]]:
        positional_args: list[str] = []
        named_args: list[tuple[str, Any]] = []

        for arg in call_args:
            if "=" not in arg:
                positional_args.append(arg)
                continue

            (named_arg_name, named_arg_val) = arg.split("=", 1)
            if named_arg_name in kw_args.argument_names:
                # It's a correct named argument
                named_args.append((named_arg_name, named_arg_val))
            else:
                positional_args.append(arg)

        return (positional_args, named_args)

    def _count_keyword_call_args(self, kw: KeywordData, call_args: Iterable[str]) -> None:
        if not kw.arguments or kw.argument_use_count is None:
            # This is a downloaded library keyword. We don't care about the args
            return
        (positional_args, named_args) = self._parse_args(call_args, kw.arguments)

        (called_with_args, called_with_kwargs) = kw.arguments.map(
            positional_args,
            named_args,
            replace_defaults=False,
        )

        called_with_kwarg_names = [a[0] for a in called_with_kwargs]
        kw_arg_names = [a for a in kw.arguments.argument_names if a not in called_with_kwarg_names]

        if len(kw_arg_names) == 0:
            return

        for position, arg in enumerate(called_with_args):
            if isinstance(arg, DefaultValue):
                continue

            if position >= len(kw_arg_names):
                position = len(kw_arg_names) - 1  # noqa: PLW2901

            arg_name = kw_arg_names[position]
            kw.argument_use_count[arg_name] += 1

        for name, val in called_with_kwargs:
            if isinstance(val, DefaultValue):
                continue
            kw.argument_use_count[name] += 1

    def _get_keyword_returns(self, node: Keyword | Block) -> bool:  # noqa: C901
        """
        Return if keyword returns a value or not.

        A return must have an explicit value.
        """
        for token in node.body:
            if isinstance(token, Block):
                # Block like `IF`, `FOR`, etc. Crawl recursively
                block_returns = self._get_keyword_returns(token)
                if block_returns is True:
                    return True
                continue

            if token.type in (
                Token.RETURN,
                Token.RETURN_STATEMENT,
            ):
                # `RETURN` and `[Return]` syntax
                if token.get_token(Token.ARGUMENT) is not None:
                    return True
                continue

            if token.type == Token.KEYWORD:
                called_keyword_name = token.get_token(Token.KEYWORD)
                if not called_keyword_name or called_keyword_name.value is None:
                    continue

                # Node is special return keywords `Return From Keyword` and `Return From Keyword If`

                keyword_name_normalized = normalize_keyword_name(called_keyword_name.value)
                if keyword_name_normalized not in (
                    "returnfromkeyword",
                    "returnfromkeywordif",
                ):
                    continue

                argument_count = len(token.get_tokens(Token.ARGUMENT))
                if keyword_name_normalized == "returnfromkeyword" and argument_count >= 1:
                    return True
                if keyword_name_normalized == "returnfromkeywordif" and argument_count >= 2:  # noqa: PLR2004
                    return True
                continue

        return False
