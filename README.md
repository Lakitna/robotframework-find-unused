# Robot Framework Find Unused

Find unused parts of your Robot Framework project.

[Robocop](https://github.com/MarketSquare/robotframework-robocop) is great at finding unused parts
in a single file. Find unused finds unused parts across all your project files.

Allows you to find unused:

- Keywords
- Keyword arguments
- Keyword return statements
- Global variables
- Files

## Installation

Install with pip

```shell
pip install robotframework-find-unused
```

## How to use

This is a command-line tool.

1. Open a command line in your Robot Framework project
2. Run the following command to show available options:

    ```shell
    robotunused --help
    ```

### Find unused keywords

![Keywords command demo gif](./docs/gif/keywords/keywords.gif)

Walk through your `.robot`, `.resource`, and `.py` files. In those files, count how often each
keyword is used (called). Keywords with 0 uses are logged.

```shell
robotunused keywords
```

Please note that there are limitations. For an overview of current limitations, run the following
command:

```shell
robotunused keywords --help
```

#### Available options

<!--<command_keywords_cli_options>-->
| flag                     | option                         | default   | description                                                                          |
| ------------------------ | ------------------------------ | --------- | ------------------------------------------------------------------------------------ |
| `-c`, `--show-count`     |                                |           | Output usage count for all keywords instead of only unused keywords                  |
| `-f`, `--filter`         | <GlobPattern>                  |           | Only output keywords who's name match the glob pattern. Match without library prefix |
| `-d`, `--deprecated`     | `include` / `exclude` / `only` | `include` | How to output deprecated keywords                                                    |
| `-p`, `--private`        | `include` / `exclude` / `only` | `include` | How to output private keywords                                                       |
| `-l`, `--library`        | `include` / `exclude` / `only` | `exclude` | How to output keywords from downloaded libraries                                     |
| `-u`, `--unused-library` | `include` / `exclude`          | `exclude` | How to output unused keywords from downloaded libraries                              |
| `-v`, `--verbose`        |                                |           | Show more log output. When provided twice: Show even more log output                 |
<!--</command_keywords_cli_options>-->

### Find unused keyword arguments

![Arguments command demo gif](./docs/gif/arguments/arguments.gif)

Walk through your `.robot`, `.resource`, and `.py` files. In those files, count how often each
argument is used during a keyword call. Arguments with 0 uses are logged.

By default, will ignore arguments from unused keywords.

```shell
robotunused arguments
```

Please note that there are limitations. For an overview of current limitations, run the following
command:

```shell
robotunused arguments --help
```

#### Available options

<!--<command_arguments_cli_options>-->
| flag                 | option                         | default   | description                                                                          |
| -------------------- | ------------------------------ | --------- | ------------------------------------------------------------------------------------ |
| `-c`, `--show-count` |                                |           | Show usage count for all arguments instead of only unused arguments                  |
| `-f`, `--filter`     | <GlobPattern>                  |           | Only output keywords who's name match the glob pattern. Match without library prefix |
| `-d`, `--deprecated` | `include` / `exclude` / `only` | `include` | How to output deprecated keywords                                                    |
| `-p`, `--private`    | `include` / `exclude` / `only` | `include` | How to output private keywords                                                       |
| `-l`, `--library`    | `include` / `exclude` / `only` | `exclude` | How to output keywords from downloaded libraries                                     |
| `-u`, `--unused`     | `include` / `exclude` / `only` | `exclude` | How to output unused keywords                                                        |
| `-v`, `--verbose`    |                                |           | Show more log output. When provided twice: Show even more log output                 |
<!--</command_arguments_cli_options>-->

### Find unused keyword return statements

![Returns command demo gif](./docs/gif/returns/returns.gif)

Walk through your `.robot`, `.resource`, and `.py` files. In those files, count how often each
keyword return value is used (assigned to a variable). Keywords whose return value is never useds
are logged.

By default, will ignore arguments from unused keywords.

```shell
robotunused returns
```

Please note that there are limitations. For an overview of current limitations, run the following
command:

```shell
robotunused returns --help
```

#### Available options

<!--<command_returns_cli_options>-->
| flag                 | option                         | default   | description                                                                          |
| -------------------- | ------------------------------ | --------- | ------------------------------------------------------------------------------------ |
| `-c`, `--show-count` |                                |           | Output usage count for all keywords instead of only keywords with unused returns     |
| `-f`, `--filter`     | <GlobPattern>                  |           | Only output keywords who's name match the glob pattern. Match without library prefix |
| `-d`, `--deprecated` | `include` / `exclude` / `only` | `include` | How to output deprecated keywords                                                    |
| `-p`, `--private`    | `include` / `exclude` / `only` | `include` | How to output private keywords                                                       |
| `-l`, `--library`    | `include` / `exclude` / `only` | `exclude` | How to output keywords from downloaded libraries                                     |
| `-u`, `--unused`     | `include` / `exclude` / `only` | `exclude` | How to output unused keywords                                                        |
| `-v`, `--verbose`    |                                |           | Show more log output. When provided twice: Show even more log output                 |
<!--</command_returns_cli_options>-->

### Find unused variables

![Variables command demo gif](./docs/gif/variables/variables.gif)

Walk through your `.robot` and `.resource` files. In those files, count how often each
variable is used. Variables defined in a variables section or variable file with 0 uses are logged.

```shell
robotunused variables
```

Please note that there are limitations. For an overview of current limitations, run the following
command:

```shell
robotunused variables --help
```

#### Available options

<!--<command_variables_cli_options>-->
| flag                 | option        | default | description                                                                                                                                                                                                                                                                                                                     |
| -------------------- | ------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-c`, `--show-count` |               |         | Show usage count for all variables instead of only unused variables                                                                                                                                                                                                                                                             |
| `-f`, `--filter`     | <GlobPattern> |         | Only show variables who's name match the glob pattern. Matching without {brackets} and $@&% prefixes                                                                                                                                                                                                                            |
| `--pythonpath`       | <path>        |         | Same as --pythonpath in Robotframework: Additional locations (directories, ZIPs) where to search libraries and other extensions when they are imported. Multiple paths can be given by separating them with a colon (`:`) or by using this option several times. Given path can also be a glob pattern matching multiple paths. |
| `-v`, `--verbose`    |               |         | Show more log output. When provided twice: Show even more log output                                                                                                                                                                                                                                                            |
<!--</command_variables_cli_options>-->

### Find unused files

![Files command demo gif](./docs/gif/files/files.gif)

For each of your `.robot` files, follow the full chain of imports. Files that are never (indirectly)
imported by a `.robot` file are logged.

```shell
robotunused files
```

Please note that there are limitations. For an overview of current limitations, run the following
command:

```shell
robotunused files --help
```

#### Available options

<!--<command_files_cli_options>-->
| flag                 | option                         | default   | description                                                                                                                                                                                                                                                                                                                     |
| -------------------- | ------------------------------ | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-c`, `--show-count` |                                |           | Output usage count for all files instead of only unused files                                                                                                                                                                                                                                                                   |
| `-t`, `--show-tree`  |                                |           | Output file import trees for every .robot file                                                                                                                                                                                                                                                                                  |
| `--tree-max-depth`   | Positive integer (x>=0)        | `0`       | Only applies when using `--show-tree`. Maximum tree depth.                                                                                                                                                                                                                                                                      |
| `--tree-max-height`  | Positive integer (x>=0)        | `0`       | Only applies when using `--show-tree`. Maximum tree height.                                                                                                                                                                                                                                                                     |
| `-f`, `--filter`     | <GlobPattern>                  |           | Only output files who's path match the glob pattern                                                                                                                                                                                                                                                                             |
| `-r`, `--resource`   | `include` / `exclude` / `only` | `include` | How to output resource file imports                                                                                                                                                                                                                                                                                             |
| `-l`, `--library`    | `include` / `exclude` / `only` | `include` | How to output (custom) library file imports                                                                                                                                                                                                                                                                                     |
| `-V`, `--variable`   | `include` / `exclude` / `only` | `include` | How to output variable file imports                                                                                                                                                                                                                                                                                             |
| `-u`, `--unused`     | `include` / `exclude` / `only` | `include` | How to output unused file imports                                                                                                                                                                                                                                                                                               |
| `--pythonpath`       | <path>                         |           | Same as --pythonpath in Robotframework: Additional locations (directories, ZIPs) where to search libraries and other extensions when they are imported. Multiple paths can be given by separating them with a colon (`:`) or by using this option several times. Given path can also be a glob pattern matching multiple paths. |
| `-v`, `--verbose`    |                                |           | Show more log output. When provided twice: Show even more log output                                                                                                                                                                                                                                                            |
<!--</command_files_cli_options>-->

## Limitations

Every command has limitations. To see an up-to-date list of limitations for each command, use the
`--help` flag. Every limitation also has a Github issue. If you find a limitation without issue,
it's a bug or knowledge gap. Please open an issue so it can be addressed.

The following is a list of generic limitations. These limitations apply to all commands.

### Generic limitation 1: Less used filetypes are ignored

Find Unused supports `.robot`, `.resource`, and `.py` files. It also supports `.json`, `.yaml`, and
`.py` variables files.

Anything else is unsupported. This includes older filetypes (like `.html` and `.tsv`) and less used
filetypes (like `.rst` and `rbt`).

### Generic limitation 2: No localization

Robot Framework supports localization. Find unused does not support it. Any language other than
English will produce unexpected results.

## Contributing

I'm open to contributions. Please contact me in the issues.

When contributing, you'll need [uv](https://docs.astral.sh/uv/) to manage dependencies.

### Linting

You can't merge with lint issues. This is enforced by the pipeline.

To run the linter, use the following command:

```shell
uv run ruff check
```

### Testing

You can't merge with failing tests. This is enforced by the pipeline.

To run all tests, use the following command:

```shell
uv run pytest -n auto
```

### Tasks

To manage various things, we use Invoke as a task runner.

To get a full list of available tasks, run:

```shell
uv run invoke --list
```

To run a task, run:

```shell
uv run invoke build
```
