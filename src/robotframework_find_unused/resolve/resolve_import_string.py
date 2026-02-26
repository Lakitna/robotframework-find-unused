import importlib.util
from abc import abstractmethod
from pathlib import Path
from typing import Literal

from robot.libraries import STDLIBS

from robotframework_find_unused.common.const import VariableValue
from robotframework_find_unused.common.path import path_exists, path_in_scope

from .resolve_variables import resolve_variables


class _AbstractImportStringResolver:
    """Base for import string resolvers"""

    @abstractmethod
    def can_handle(self, import_str: str) -> bool:
        """Return True if it makes sense to call resolve()"""
        raise NotImplementedError

    @abstractmethod
    def resolve(
        self,
        import_str: str,
        relative_to: Path,
        discovered_files: set[Path],
        in_scope_directory: Path,
    ) -> Path | Literal[False] | None:
        """
        Resolve import string.

        Returns one of:
        - File path
        - `False` when a file is found, but out of scope
        - `None` when resolve did not yield a file.
        """
        raise NotImplementedError


class _StandardLibResolver(_AbstractImportStringResolver):
    def __init__(self) -> None:
        self.stdlibs = set()
        for lib in STDLIBS:
            self.stdlibs.add(lib.casefold())

    def can_handle(self, import_str: str) -> bool:
        return import_str.casefold() in self.stdlibs

    def resolve(
        self,
        import_str: str,  # noqa: ARG002
        relative_to: Path,  # noqa: ARG002
        discovered_files: set[Path],  # noqa: ARG002
        in_scope_directory: Path,  # noqa: ARG002
    ) -> Path | None | Literal[False]:
        return False


class _FilePathResolver(_AbstractImportStringResolver):
    def can_handle(self, import_str: str) -> bool:
        if "/" in import_str or "\\" in import_str:
            return True

        return "." in import_str

    def resolve(
        self,
        import_str: str,
        relative_to: Path,
        discovered_files: set[Path],
        in_scope_directory: Path,
    ) -> Path | Literal[False] | None:
        abs_path = relative_to.joinpath(import_str).resolve()

        if not path_in_scope(abs_path, in_scope_directory):
            return False

        if abs_path in discovered_files:
            return abs_path

        if path_exists(abs_path):
            return abs_path

        return None


class _ModulePathResolver(_AbstractImportStringResolver):
    def can_handle(self, import_str: str) -> bool:
        return "/" not in import_str and "\\" not in import_str

    def resolve(
        self,
        import_str: str,
        relative_to: Path,  # noqa: ARG002
        discovered_files: set[Path],
        in_scope_directory: Path,
    ) -> Path | Literal[False] | None:
        module_import_options = [import_str]
        if "." in import_str:
            module_import_options.append(import_str.rsplit(".", maxsplit=1)[0])

        lib_path = None
        for opt in module_import_options:
            lib_path = self._resolve_module_path(opt)
            if not lib_path:
                continue

            if not path_in_scope(lib_path, in_scope_directory):
                return False

            if lib_path in discovered_files:
                return lib_path

            if path_exists(lib_path):
                return lib_path

            # Found, but out of scope
            return False

        return None

    def _resolve_module_path(self, import_str: str) -> Path | None:
        try:
            spec = importlib.util.find_spec(*import_str.rsplit(".", maxsplit=1))
        except (ModuleNotFoundError, ImportError):
            # Is bad import or downloaded library
            return None

        if not spec or not spec.origin:
            return None

        return Path(spec.origin)


_resolve_strategies: tuple[_AbstractImportStringResolver, ...] = (
    _StandardLibResolver(),
    _FilePathResolver(),
    _ModulePathResolver(),
)


def resolve_import_string(
    import_str: str,
    relative_to: Path,
    in_scope_directory: Path,
    discovered_files: set[Path] | None = None,
) -> Path | None:
    """
    Resolve a file import string.

    Returns absolute Path.

    Raises ImportError when import can't be resolved.
    """
    if discovered_files is None:
        discovered_files = set()

    variables = {
        "curdir": VariableValue(normalized_name="curdir", value="."),
    }
    (import_str, _) = resolve_variables(import_str, variables)

    for strat in _resolve_strategies:
        if not strat.can_handle(import_str):
            continue

        resolved = strat.resolve(
            import_str,
            relative_to,
            discovered_files,
            in_scope_directory,
        )

        if resolved:
            return resolved

        if resolved is False:
            # Resolved to file, but out of scope
            return None

    msg = f"Could not import '{import_str}' from '{relative_to}'"
    raise ImportError(msg)
