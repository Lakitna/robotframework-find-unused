from dataclasses import dataclass


@dataclass
class VariableOptions:
    """
    Command line options for the 'variables' command
    """

    show_all_count: bool
    filter_glob: str | None
    verbose: int
    pythonpath: list[str]
    source_path: str
