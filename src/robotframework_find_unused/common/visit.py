from functools import cache
from pathlib import Path
from typing import Literal, TypeAlias

import robot.api.parsing

RobotFileSectionName: TypeAlias = Literal[
    "comments",
    "settings",
    "variables",
    "keywords",
    "test cases",
    "tasks",
]


class SectionsList(list[RobotFileSectionName]):
    """Hashable list for Robot Framework `*** Section ***` names"""

    def __hash__(self) -> int:  # pyright: ignore[reportIncompatibleVariableOverride]  # noqa: D105
        return hash("|".join(iter(self)))


def visit_robot_files(
    file_paths: list[Path],
    visitor: robot.api.parsing.ModelVisitor,
    parse_sections: list[RobotFileSectionName] | Literal["all"] = "all",
):
    """
    Use Robotframework to traverse files with a visitor.

    See Robotframework docs on Visitors for details.
    """
    if isinstance(parse_sections, list):
        parse_sections = SectionsList(parse_sections)

    for file_path in file_paths:
        model = parse_robot_file(file_path, parse_sections)
        visitor.visit(model)


@cache
def parse_robot_file(file_path: Path, parse_sections: SectionsList | Literal["all"] = "all"):
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


def _get_partial_file_content(file_path: Path, parse_sections: SectionsList) -> str:
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
