# Robot Framework Find Unused

Find unused parts of your Robot Framework project.

[Robocop](https://github.com/MarketSquare/robotframework-robocop) is great at finding unused parts
in a single file. Find unused finds unused parts across all your project files.

Allows you to find unused:

- Keywords
- Keyword arguments
- Keyword return statements
- Global variables

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

Walk through your `.robot`, `.resource`, and `.py` files. In those files, count how often each
keyword is used (called). Keywords with 0 uses are logged.

By default, will ignore keywords from downloaded libraries.

```shell
robotunused keywords
```

Please note that there are limitations. For an overview of current limitations, run the following
command:

```shell
robotunused keywords --help
```

#### Available options

| flag                 | option                         | default   | description                                                                          |
|----------------------|--------------------------------|-----------|--------------------------------------------------------------------------------------|
| `-c`, `--show-count` |                                |           | Output usage count for all keywords instead of only unused keywords                  |
| `-f`, `--filter`     | Globlike pattern               |           | Only output keywords who's name match the glob pattern. Match without library prefix |
| `-d`, `--deprecated` | `include` / `exclude` / `only` | `include` | How to output deprecated keywords                                                    |
| `-p`, `--private`    | `include` / `exclude` / `only` | `include` | How to output private keywords                                                       |
| `-l`, `--library`    | `include` / `exclude` / `only` | `exclude` | How to output keywords from downloaded libraries                                     |
| `-v`, `--verbose`    |                                |           | Show more log output                                                                 |

### Find unused keyword arguments

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

| flag                 | option                         | default   | description                                                                                        |
|----------------------|--------------------------------|-----------|----------------------------------------------------------------------------------------------------|
| `-c`, `--show-count` |                                |           | Show usage count for all arguments instead of only unused arguments                                |
| `-f`, `--filter`     | Globlike pattern               |           | Only output arguments for keywords who's name match the glob pattern. Match without library prefix |
| `-d`, `--deprecated` | `include` / `exclude` / `only` | `include` | How to output deprecated keywords                                                                  |
| `-p`, `--private`    | `include` / `exclude` / `only` | `include` | How to output private keywords                                                                     |
| `-l`, `--library`    | `include` / `exclude` / `only` | `exclude` | How to output keywords from downloaded libraries                                                   |
| `-v`, `--verbose`    |                                |           | Show more log output                                                                               |

### Find unused keyword return statements

Walk through your `.robot`, `.resource`, and `.py` files. In those files, count how often each
keyword return value is used (assigned to a variable). Keywords whose return value is never useds
are logged.

By default, will ignore keywords from downloaded libraries.

```shell
robotunused returns
```

Please note that there are limitations. For an overview of current limitations, run the following
command:

```shell
robotunused returns --help
```

#### Available options

| flag                 | option                         | default   | description                                                                          |
|----------------------|--------------------------------|-----------|--------------------------------------------------------------------------------------|
| `-c`, `--show-count` |                                |           | Output usage count for all keywords instead of only keywords with unused returns     |
| `-f`, `--filter`     | Globlike pattern               |           | Only output keywords who's name match the glob pattern. Match without library prefix |
| `-d`, `--deprecated` | `include` / `exclude` / `only` | `include` | How to output deprecated keywords                                                    |
| `-p`, `--private`    | `include` / `exclude` / `only` | `include` | How to output private keywords                                                       |
| `-l`, `--library`    | `include` / `exclude` / `only` | `exclude` | How to output keywords from downloaded libraries                                     |
| `-v`, `--verbose`    |                                |           | Show more log output                                                                 |

### Find unused global variables

Walk through your `.robot` and `.resource` files. In those files, count how often each
variable is used. Variables defined in a variables section with 0 uses are logged.

```shell
robotunused variables
```

Please note that there are limitations. For an overview of current limitations, run the following
command:

```shell
robotunused variables --help
```

#### Available options

| flag                 | option           | default | description                                                                                         |
|----------------------|------------------|---------|-----------------------------------------------------------------------------------------------------|
| `-c`, `--show-count` |                  |         | Show usage count for all variables instead of only unused variables                                 |
| `-f`, `--filter`     | Globlike pattern |         | Only show variables who's name match the glob pattern. Matching without {brackets} and $@& prefixes |
| `-v`, `--verbose`    |                  |         | Show more log output                                                                                |

## Contributing

I'm open to contributions. Please contact me in the issues.

When contibuting, you'll need [Poetry](https://python-poetry.org/) to manage dependencies.

Please ensure that you install the develop dependencies as well as the regular dependencies by
running the following command:

```shell
poetry install --with dev
```

### Linting

You can't merge with lint issues. This is enforced by the pipeline.

To run the linter, use the following command:

```shell
poetry run ruff check
```

### Testing

You can't merge with failing tests. This is enforced by the pipeline.

To run all tests, use the following command:

```shell
poetry run pytest
```
