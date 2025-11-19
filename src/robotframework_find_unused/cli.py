"""
CLI entry point
"""

# ruff: noqa: FBT001,D301

import sys

import click

from robotframework_find_unused.commands import (
    ArgumentsOptions,
    KeywordOptions,
    ReturnOptions,
    VariableOptions,
    cli_arguments,
    cli_keywords,
    cli_returns,
    cli_variables,
)
from robotframework_find_unused.common.const import KeywordFilterOption

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
    deprecated: KeywordFilterOption,
    private: KeywordFilterOption,
    library: KeywordFilterOption,
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
        "Matching without {brackets} and $@& prefixes"
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
    Find unused variables defined in a variables section

    Traverse files in the given file path. In those files, count how often each variable is used.
    Variables defined in a variables section with 0 uses are logged.

    ----------

    Limitation 1: Only variables defined in a variables section.

    All of the following variables are ignored:

    \b
    - Variables only defined in a variables file
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

    ----------

    Limitation 2: Variable names containing variables are ignored.

    When defining a variable, the variable name can contain other variables. These variables are
    ignored and can therefore not be flagged as unused.

    Example: The variable ${helloWorld} (resolved from ${hello${place}}) is ignored.

    \b
        *** Variables ***
        ${place}    World
        ${hello${place}}    Hello World!

    ----------

    Limitation 3: Variable usage containing variables are not counted.

    When using a variable, the variable name can contain other variables. These variables are not
    counted.

    Example: ${hello${place}} is ignored. Because of this, the variable ${helloWorld} will be
    falsely flagged as unused.

    \b
        *** Variables ***
        ${helloWorld}    Hello World!

    \b
        *** Keywords ***
        My Amazing Keyword
            ${place} =    Set Variable    World
            Log    ${hello${place}}

    ----------

    Limitation 4: Variable names with embedded python are ignored.

    Sometimes variable names can contain python calls. Robotframework call this the extended
    variable syntax. Extended variable syntax is not supported. This should never be an issue with
    global variables.

    Example: The variable ${response} is not counted because ${response.json()} is not supported.

    \b
        *** Keywords ***
        My Amazing Keyword
            ${response} =    GET    ${someUrl}
            RETURN    ${response.json()}
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
    deprecated: KeywordFilterOption,
    private: KeywordFilterOption,
    unused: KeywordFilterOption,
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
        library_keywords="exclude",
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
    deprecated: KeywordFilterOption,
    private: KeywordFilterOption,
    library: KeywordFilterOption,
    unused: KeywordFilterOption,
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

    ----------

    Limitation 2: Library keywords are ignored.

    Any keyword defined in a Python file is ignored.
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
