from robocop import Config
from robocop.files import get_files
from robot.errors import DataError
from robot.libdoc import LibraryDocumentation
from robot.libdocpkg.model import LibraryDoc


def find_files_with_libdoc(robocop_config: Config):
    """
    Gather files in the given scope with LibDoc

    Libdoc supports .robot, .resource, .py, and downloaded libs
    """
    file_paths = [p for p in get_files(robocop_config)]

    files: list[LibraryDoc] = []
    for file in file_paths:
        try:
            libdoc = LibraryDocumentation(file)
        except DataError:
            continue
        if not isinstance(libdoc, LibraryDoc):
            continue

        files.append(libdoc)
    return files
