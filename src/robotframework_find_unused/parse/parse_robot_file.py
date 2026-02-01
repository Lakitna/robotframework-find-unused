from functools import cache
from pathlib import Path
from typing import Literal, TypeAlias

import robot.api.parsing

# Limitation: No localisation
RobotFileSectionName: TypeAlias = Literal[
    "comments",
    "settings",
    "variables",
    "keywords",
    "test cases",
    "tasks",
]


@cache
def parse_robot_file(
    file_path: Path,
    parse_sections: tuple[RobotFileSectionName, ...] | Literal["all"] = "all",
):
    """
    Parse a file using the Robot parser.

    Can skip entire sections but keeps the section headers.
    """
    if parse_sections == "all" or file_path.suffix.lower() not in [".robot", ".resource"]:
        return robot.api.parsing.get_model(file_path, data_only=True)

    file_content = _get_partial_file_content(file_path, parse_sections)
    model = robot.api.parsing.get_model(file_content, data_only=True)
    model.source = file_path
    return model


def _get_partial_file_content(
    file_path: Path,
    parse_sections: tuple[RobotFileSectionName, ...] | Literal["all"],
) -> str:
    """
    Get partial raw file content.

    Output is a .robot or .resource file with only specific *** sections ***. Section headers are
    always included.
    """
    with file_path.open(encoding="utf8") as f:
        raw_file_content = f.readlines()

    file_content = ""
    cur_section = None
    for line in raw_file_content:
        if line.startswith("***"):
            cur_section = line.strip("* \n").lower()

            # Limitation: No localisation
            if not cur_section.endswith("s"):
                # Is an old singular section header. Make plural
                cur_section += "s"

            # Always keep section headings
            file_content += line
            continue

        if cur_section and cur_section not in parse_sections:
            continue

        file_content += line

    return file_content
