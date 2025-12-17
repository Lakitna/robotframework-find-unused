from functools import cache
from pathlib import Path
from typing import Literal

import robot.api.parsing


class SectionsList(list):
    def __hash__(self) -> int:  # pyright: ignore[reportIncompatibleVariableOverride]  # noqa: D105
        return hash("|".join(iter(self)))


def visit_robot_files(
    file_paths: list[Path],
    visitor: robot.api.parsing.ModelVisitor,
    parse_sections: list[str] | Literal["all"] = "all",
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

    Can skip entire sections.
    """
    if parse_sections == "all" or file_path.suffix.lower() not in [".robot", ".resource"]:
        return robot.api.parsing.get_model(file_path, data_only=True)

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

        if cur_section and cur_section not in parse_sections:
            continue

        file_content += line

    model = robot.api.parsing.get_model(file_content, data_only=True)
    model.source = file_path
    return model
