"""
CLI entry point
"""

# ruff: noqa: FBT001,D301

import sys

import click

from .commands import (
    ArgumentsOptions,
    FileOptions,
    KeywordOptions,
    ReturnOptions,
    VariableOptions,
    cli_arguments,
    cli_files,
    cli_keywords,
    cli_returns,
    cli_variables,
)
from .common.const import FilterOption

click_choice_keyword_filter_option = click.Choice(
    ["include", "exclude", "only"],
    case_sensitive=False,
)


@click.group(
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
)
def cli():
    """
    Find unused parts of your Robot Framework project.
    """


@cli.command(name="keywords")
@click.option(
    "-c",
    "--show-count",
    default=False,
    is_flag=True,
    help="Output usage count for all keywords instead of only unused keywords",
)
@click.option(
    "-f",
    "--filter",
    default=None,
    metavar="<GLOB>",
    help="Only output keywords who's name match the glob pattern. Match without library prefix",
)
@click.option(
    "-d",
    "--deprecated",
    type=click_choice_keyword_filter_option,
    default="include",
    show_default=True,
    help="How to output deprecated keywords",
)
@click.option(
    "-p",
    "--private",
    type=click_choice_keyword_filter_option,
    default="include",
    show_default=True,
    help="How to output private keywords",
)
@click.option(
    "-l",
    "--library",
    type=click_choice_keyword_filter_option,
    default="exclude",
    show_default=True,
    help="How to output keywords from downloaded libraries",
)
@click.option(
    "-u",
    "--unused-library",
    type=click.Choice(["include", "exclude"], case_sensitive=False),
    default="exclude",
    show_default=True,
    help="How to output unused keywords from downloaded libraries",
)
@click.option(
    "-v",
    "--verbose",
    default=False,
    count=True,
    help="Show more log output. Can be used twice",
)
@click.argument("file_path", default=".")
def keywords(  # noqa: PLR0913
    show_count: bool,
    filter: str | None,  # noqa: A002
    deprecated: FilterOption,
    private: FilterOption,
    library: FilterOption,
    unused_library: FilterOption,
    verbose: int,
    file_path: str,
):
    """
    Find unused keywords

    Traverse files in the given file path. In those files, count how often each keyword is used.
    Keywords with 0 uses are logged.

    ----------

    Limitation 1: Keywords with embedded arguments are not counted

    Example: This keyword is not counted because it contains the embedded argument ${something}:

    \b
        Do ${something} amazing

    ----------

    Limitation 2: Library prefixes are ignored.

    Example: The following keywords are counted as the same keyword:

    \b
        SeleniumLibrary.Get Text
        AppiumLibrary.Get Text

    ----------

    Limitation 3: Most keywords used as an argument for another keyword are counted, but some may
    not be.

    Example: 'Beautiful keyword' is not counted.

    \b
        Do Something Amazing    ${True}    Beautiful keyword

    To ensure that your keyword in an argument is counted, your keyword name or argument name
    must include the literal word 'keyword' (case insensitive).

    Example: 'Beautiful keyword' is counted, because 'Run Keyword' includes the word 'keyword'

    \b
        Run Keyword    Beautiful keyword

    Example: 'Beautiful keyword' is counted, because the argument ${inner_keyword} includes the word
    'keyword'

    \b
        Amazing    ${True}    inner_keyword=Beautiful keyword
    """
    options = KeywordOptions(
        source_path=file_path,
        deprecated_keywords=deprecated,
        private_keywords=private,
        library_keywords=library,
        unused_library_keywords=unused_library,
        keyword_filter_glob=filter,
        show_all_count=show_count,
        verbose=verbose,
    )
    exit_code = cli_keywords(options)
    sys.exit(exit_code)


@cli.command(name="variables")
@click.option(
    "-c",
    "--show-count",
    default=False,
    is_flag=True,
    help="Show usage count for all variables instead of only unused variables",
)
@click.option(
    "-f",
    "--filter",
    default=None,
    metavar="<GLOB>",
    help=(
        "Only show variables who's name match the glob pattern. "
        "Matching without {brackets} and $@&% prefixes"
    ),
)
@click.option(
    "-v",
    "--verbose",
    default=False,
    count=True,
    help="Show more log output. Can be used twice",
)
@click.argument("file_path", default=".")
def variables(
    show_count: bool,
    filter: str | None,  # noqa: A002
    verbose: int,
    file_path: str,
):
    """
    Find unused global variables

    Traverse files in the given file path. In those files, count how often each global variable is
    used. Variables defined in a variables section or variable file with 0 uses are logged.

    ----------

    Limitation 1: Only globally user-defined variables.

    All of the following variables are ignored:

    \b
    - Variables only provided via the command line
    - Environment variables
    - BuiltIn variables
    - Variables only set with `Set Global Variable`
    - Variables only set with `VAR  ...  scope=GLOBAL`
    - Variables only set with `Set Suite Variable`
    - Variables only set with `VAR  ...  scope=SUITE`
    - Variables only set with `Set Test Variable`
    - Variables only set with `VAR  ...  scope=TEST`
    - Variables only set with `Set Task Variable`
    - Variables only set with `VAR  ...  scope=TASK`
    - Variables only set with `Set Variable`
    - Variables only set with `VAR  ...`
    - Variables only set with the return value of a keyword

    ----------

    Limitation 2: Variables with variables in their name are not always counted.

    When using or defining a variable, the variable name can contain other variables. The most
    common usecases are supported but there are a lot of possible complexity which is not supported.

    Variables in variable names are only counted when:

    \b
    - None of the involved variables are limited by limitation 1.
    - All nested variables are single-line scalar variables.
      - No lists (e.g. `@{example}`)
      - No dicts (e.g. `&{example}`)
      - No multi-line string definitions
    - No extended variable syntax.

    Example: ${hello_${place.lower()}} uses extended variable syntax and is therefore ignored.
    Because of this, the variable ${hello_world} will be falsely flagged as unused.

    \b
        *** Variables ***
        ${hello_world}    Hello World!
        ${place}          WORLD

    \b
        *** Keywords ***
        My Amazing Keyword
            Log    ${hello_${place.lower()}}

    ----------

    Limitation 3: Only counts variable uses in `.robot` and `.resource` files.

    Using variables in Python files is never counted. This is true for both libraries and Python
    variable files.

    Example: The use of the variable `person` is not counted because it's used in a Python variable
    file.

    \b
        person = "Pekka"
        message = "Hello " + person
    """
    options = VariableOptions(
        source_path=file_path,
        show_all_count=show_count,
        filter_glob=filter,
        verbose=verbose,
    )
    exit_code = cli_variables(options)
    sys.exit(exit_code)


@cli.command(name="arguments")
@click.option(
    "-c",
    "--show-count",
    default=False,
    is_flag=True,
    help="Show usage count for all arguments instead of only unused arguments",
)
@click.option(
    "-f",
    "--filter",
    default=None,
    metavar="<GLOB>",
    help="Only output keywords who's name match the glob pattern. Match without library prefix",
)
@click.option(
    "-d",
    "--deprecated",
    type=click_choice_keyword_filter_option,
    default="include",
    show_default=True,
    help="How to output deprecated keywords",
)
@click.option(
    "-p",
    "--private",
    type=click_choice_keyword_filter_option,
    default="include",
    show_default=True,
    help="How to output private keywords",
)
@click.option(
    "-l",
    "--library",
    type=click_choice_keyword_filter_option,
    default="exclude",
    show_default=True,
    help="How to output keywords from downloaded libraries",
)
@click.option(
    "-u",
    "--unused",
    type=click_choice_keyword_filter_option,
    default="exclude",
    show_default=True,
    help="How to output unused keywords",
)
@click.option(
    "-v",
    "--verbose",
    default=False,
    count=True,
    help="Show more log output. Can be used twice",
)
@click.argument("file_path", default=".")
def arguments(  # noqa: PLR0913
    show_count: bool,
    filter: str | None,  # noqa: A002
    deprecated: FilterOption,
    private: FilterOption,
    library: FilterOption,
    unused: FilterOption,
    verbose: int,
    file_path: str,
):
    """
    Find unchanged default keyword arguments

    Traverse files in the given file path. In those files, count how often each argument is used
    during a keyword call. Arguments with 0 uses are logged.

    ----------

    Limitation 1: Arguments for keywords with embedded arguments are not counted

    Example: The argument ${beautiful} is not counted because the keyword contains the embedded
    argument ${something}:

    \b
        Do ${something} amazing
            [Arguments]    ${beautiful}=${True}

    ----------

    Limitation 2: Most keywords used as an argument for another keyword are counted, but some may
    not be. This includes the arguments used by the inner keyword.

    Example: 'Beautiful keyword' is not recognized as a keyword. Because of this, the ${hello}
    argument of 'Beautiful keyword' is falsely counted as an argument for 'Do Something Amazing'.

    \b
        Do Something Amazing    Beautiful keyword    hello=${True}

    To ensure that your keyword is handled properly, your keyword name or argument name must include
    the literal word 'keyword' (case insensitive).

    Example: The ${hello} argument of 'Beautiful keyword' is counted, because 'Run Keyword' includes
    the word 'keyword'

    \b
        Run Keyword    Beautiful keyword    hello=${True}

    Example: The ${hello} argument of 'Beautiful keyword' is counted, because the argument
    ${inner_keyword} includes the word 'keyword'.

    \b
        Amazing    inner_keyword=Beautiful keyword    hello=${True}

    Note how the script assumes that all arguments after ${inner_keyword} are arguments for
    'Beautiful keyword'.
    """
    options = ArgumentsOptions(
        source_path=file_path,
        deprecated_keywords=deprecated,
        private_keywords=private,
        library_keywords=library,
        unused_keywords=unused,
        keyword_filter_glob=filter,
        show_all_count=show_count,
        verbose=verbose,
    )
    exit_code = cli_arguments(options)
    sys.exit(exit_code)


@cli.command(name="returns")
@click.option(
    "-c",
    "--show-count",
    default=False,
    is_flag=True,
    help="Output usage count for all keywords instead of only keywords with unused returns",
)
@click.option(
    "-f",
    "--filter",
    default=None,
    metavar="<GLOB>",
    help="Only output keywords who's name match the glob pattern. Match without library prefix",
)
@click.option(
    "-d",
    "--deprecated",
    type=click_choice_keyword_filter_option,
    default="include",
    show_default=True,
    help="How to output deprecated keywords",
)
@click.option(
    "-p",
    "--private",
    type=click_choice_keyword_filter_option,
    default="include",
    show_default=True,
    help="How to output private keywords",
)
@click.option(
    "-l",
    "--library",
    type=click_choice_keyword_filter_option,
    default="exclude",
    show_default=True,
    help="How to output keywords from downloaded libraries",
)
@click.option(
    "-u",
    "--unused",
    type=click_choice_keyword_filter_option,
    default="exclude",
    show_default=True,
    help="How to output unused keywords",
)
@click.option(
    "-v",
    "--verbose",
    default=False,
    count=True,
    help="Show more log output. Can be used twice",
)
@click.argument("file_path", default=".")
def returns(  # noqa: PLR0913
    show_count: bool,
    filter: str | None,  # noqa: A002
    deprecated: FilterOption,
    private: FilterOption,
    library: FilterOption,
    unused: FilterOption,
    verbose: int,
    file_path: str,
):
    """
    Find unused keyword return values

    Traverse files in the given file path. In those files, count how often each keyword return
    value is used. Keywords whose return value is never used are logged.

    ----------

    Limitation 1: Return value not counted when the keyword is used as an argument for another
    keyword.

    Example: The return value of 'Beautiful keyword' is not counted.

    \b
        ${returned_value} =    Run Keyword    Beautiful keyword

    This situation can't be counted without knowing what exactly `Run Keyword` does.
    """
    options = ReturnOptions(
        source_path=file_path,
        deprecated_keywords=deprecated,
        private_keywords=private,
        library_keywords=library,
        unused_keywords=unused,
        keyword_filter_glob=filter,
        show_all_count=show_count,
        verbose=verbose,
    )
    exit_code = cli_returns(options)
    sys.exit(exit_code)


@cli.command(name="files")
@click.option(
    "-c",
    "--show-count",
    default=False,
    is_flag=True,
    help="Output usage count for all files instead of only unused files",
)
@click.option(
    "-t",
    "--show-tree",
    default=False,
    is_flag=True,
    help="Output file import trees for every .robot file",
)
@click.option(
    "--tree-max-depth",
    default=-1,
    type=click.IntRange(min=-1, clamp=True),
    help="Only applies when using `--show-tree`. Maximum tree depth.",
)
@click.option(
    "--tree-max-height",
    default=-1,
    type=click.IntRange(min=-1, clamp=True),
    help="Only applies when using `--show-tree`. Maximum tree height.",
)
@click.option(
    "-f",
    "--filter",
    default=None,
    metavar="<GLOB>",
    help="Only output files who's path match the glob pattern",
)
@click.option(
    "-r",
    "--resource",
    type=click_choice_keyword_filter_option,
    default="include",
    show_default=True,
    help="How to output resource file imports",
)
@click.option(
    "-l",
    "--library",
    type=click_choice_keyword_filter_option,
    default="include",
    show_default=True,
    help="How to output (custom) library file imports",
)
@click.option(
    "-V",
    "--variable",
    type=click_choice_keyword_filter_option,
    default="include",
    show_default=True,
    help="How to output variable file imports",
)
@click.option(
    "-u",
    "--unused",
    type=click_choice_keyword_filter_option,
    default="include",
    show_default=True,
    help="How to output unused file imports",
)
@click.option(
    "-v",
    "--verbose",
    default=False,
    count=True,
    help="Show more log output. Can be used twice",
)
@click.argument("file_path", default=".")
def files(  # noqa: PLR0913
    show_count: bool,
    show_tree: bool,
    tree_max_depth: int,
    tree_max_height: int,
    filter: str | None,  # noqa: A002
    resource: FilterOption,
    library: FilterOption,
    variable: FilterOption,
    unused: FilterOption,
    verbose: int,
    file_path: str,
):
    """
    Find unused files

    Traverse files in the given file path. For all .robot files, figure out which files it uses. Log
    files that are never used.

    ----------

    Limitation 1: Downloaded libraries are ignored

    Imports to downloaded libraries are ignored. Because of this, unused downloaded libraries are
    not detected.

    Example: The unused library 'SeleniumLibrary' is not detected.

    \b
        *** Settings ***
        Library    Browser

    ----------

    Limitation 2: No Python module syntax

    Libraries can be imported with both a path-like syntax (e.g. ./foo/bar.resource) and Python
    module syntax (e.g. foo.bar). Python module syntax is not supported.

    This does not impact Resource file imports.

    Example: The custom library 'TestLibrary' is ignored since it's imported using the Python module
    syntax.

    \b
        *** Settings ***
        Resource    my.package.TestLibrary

    ----------

    Limitation 3: Imports in python files are ignored

    Only imports in `.robot` and `.resource` files are considered. Imports in other files are
    ignored.

    Example: The Python file `hello.py` is ignored since it's imported from a Python file.

    \b
        from hello import hello_world
    """
    options = FileOptions(
        path_filter_glob=filter,
        show_all_count=show_count,
        library_files=library,
        variable_files=variable,
        resource_files=resource,
        unused_files=unused,
        show_tree=show_tree,
        tree_max_depth=tree_max_depth,
        tree_max_height=tree_max_height,
        verbose=verbose,
        source_path=file_path,
    )
    exit_code = cli_files(options)
    sys.exit(exit_code)
