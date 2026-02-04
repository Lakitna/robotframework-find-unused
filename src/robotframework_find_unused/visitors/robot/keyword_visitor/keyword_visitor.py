from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Literal

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

from .keyword_definition_manager import KeywordDefinitionManager


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

    kw_matcher: KeywordDefinitionManager

    def __init__(
        self,
        custom_keywords: list[KeywordData],
        downloaded_library_keywords: list[LibraryData],
    ) -> None:
        self.kw_matcher = KeywordDefinitionManager(custom_keywords, downloaded_library_keywords)

    @property
    def keywords(self):  # noqa: D102
        return self.kw_matcher.keywords

    def visit_File(self, node: File):  # noqa: N802
        """Visit new file"""
        self.suite_template_keyword = None

        return self.generic_visit(node)

    def visit_Keyword(self, node: Keyword):  # noqa: N802
        """Keyword definition"""
        keyword = self.kw_matcher.get_keyword_definition(node.name)
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
        keyword = self.kw_matcher.get_keyword_definition(name)
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

        keyword_definition = self.kw_matcher.search_keyword_definition(arg_val)
        if not keyword_definition:
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
