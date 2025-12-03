from pathlib import Path

import robot.errors
from robot.libdoc import LibraryDocumentation
from robot.libdocpkg.model import LibraryDoc


def find_files_with_libdoc(file_paths: list[Path]):
    """
    Gather files in the given scope with LibDoc

    Libdoc supports .robot, .resource, .py, and downloaded libs
    """
    files: list[LibraryDoc] = []
    errors: list[str] = []
    for file in file_paths:
        try:
            libdoc = LibraryDocumentation(file)
            files.append(libdoc)
        except robot.errors.DataError as e:
            errors.append(e.message.split("\n", maxsplit=1)[0])
            continue
        if not isinstance(libdoc, LibraryDoc):
            continue

    return (files, errors)
