import importlib.util
from abc import abstractmethod
from pathlib import Path
from typing import Literal

from robot.libraries import STDLIBS

from robotframework_find_unused.common.const import VariableValue

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
        available_files: set[Path],
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
        available_files: set[Path],  # noqa: ARG002
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
        available_files: set[Path],
    ) -> Path | Literal[False] | None:
        abs_path = relative_to.joinpath(import_str).resolve()
        if abs_path in available_files:
            return abs_path

        # TODO: delete. Try in different projecct first to see performance impact
        # print("File system check", import_str)
        if abs_path.exists():
            return False

        return None


class _ModulePathResolver(_AbstractImportStringResolver):
    def can_handle(self, import_str: str) -> bool:
        return "/" not in import_str and "\\" not in import_str

    def resolve(
        self,
        import_str: str,
        relative_to: Path,  # noqa: ARG002
        available_files: set[Path],
    ) -> Path | Literal[False] | None:
        module_import_options = [import_str]
        if "." in import_str:
            module_import_options.append(import_str.rsplit(".", maxsplit=1)[0])

        lib_path = None
        for opt in module_import_options:
            lib_path = self._resolve_module_path(opt)
            if not lib_path:
                continue

            if lib_path in available_files:
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
    available_files: set[Path],
) -> Path | None:
    """
    Resolve a file import string.

    Returns absolute Path.

    Raises ImportError when import_str can't be resolved.
    """
    variables = {
        "curdir": VariableValue(normalized_name="curdir", value="."),
    }
    (import_str, _) = resolve_variables(import_str, variables)

    for strat in _resolve_strategies:
        if not strat.can_handle(import_str):
            continue

        resolved = strat.resolve(import_str, relative_to, available_files)

        if resolved:
            return resolved

        if resolved is False:
            # Resolved to file, but out of scope
            return None

    msg = f"Could not import '{import_str}' from '{relative_to}'"
    raise ImportError(msg)
