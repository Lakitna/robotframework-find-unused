import importlib.util
import sys
from abc import abstractmethod
from pathlib import Path
from typing import Literal

from robot.libraries import STDLIBS

from robotframework_find_unused.common.const import ResolvedFileImport, VariableValue
from robotframework_find_unused.common.path import path_exists, path_in_scope, path_in_venv

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
    ) -> ResolvedFileImport | Literal[False] | None:
        """
        Resolve import string.

        Returns one of:
        - Resolved file path
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
        import_str: str,
        relative_to: Path,  # noqa: ARG002
        discovered_files: set[Path],  # noqa: ARG002
        in_scope_directory: Path,  # noqa: ARG002
    ) -> ResolvedFileImport | Literal[False] | None:
        resolved = _resolve_module_path(
            f"robot.libraries.{import_str}.{import_str}",
        )

        if not resolved:
            return resolved

        return ResolvedFileImport(
            type="BUILTIN",
            import_string=import_str,
            path=resolved,
        )


class _FilePathResolver(_AbstractImportStringResolver):
    _pythonpath_paths_in_scope: list[Path] | None = None

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
    ) -> ResolvedFileImport | Literal[False] | None:
        pythonpath_paths_in_scope = self._get_pythonpath_paths_in_scope(in_scope_directory)
        relative_to_paths = [relative_to, *pythonpath_paths_in_scope]

        for relative_to_path in relative_to_paths:
            abs_path = relative_to_path.joinpath(import_str).resolve()

            if not path_in_scope(abs_path, in_scope_directory):
                return False

            resolved = ResolvedFileImport(
                type="FILE_PATH",
                import_string=import_str,
                path=abs_path,
            )

            if resolved.path in discovered_files:
                return resolved

            if path_exists(resolved.path):
                return resolved

        return None

    def _get_pythonpath_paths_in_scope(self, in_scope_directory: Path) -> list[Path]:
        if self._pythonpath_paths_in_scope is not None:
            return self._pythonpath_paths_in_scope

        self._pythonpath_paths_in_scope = []
        for p in sys.path:
            path = Path(p)
            if path_in_scope(path, in_scope_directory):
                self._pythonpath_paths_in_scope.append(path)

        return self._pythonpath_paths_in_scope


class _ModulePathResolver(_AbstractImportStringResolver):
    def can_handle(self, import_str: str) -> bool:
        return "/" not in import_str and "\\" not in import_str

    def resolve(
        self,
        import_str: str,
        relative_to: Path,  # noqa: ARG002
        discovered_files: set[Path],
        in_scope_directory: Path,
    ) -> ResolvedFileImport | Literal[False] | None:
        module_import_options = [import_str]
        if "." in import_str:
            module_import_options.append(import_str.rsplit(".", maxsplit=1)[0])

        for opt in module_import_options:
            abs_path = _resolve_module_path(opt)
            if not abs_path:
                continue

            if path_in_venv(abs_path):
                return ResolvedFileImport(
                    type="DOWNLOADED_LIBRARY",
                    import_string=import_str,
                    path=abs_path,
                )

            resolved = ResolvedFileImport(
                type="MODULE",
                import_string=import_str,
                path=abs_path,
            )

            if not path_in_scope(resolved.path, in_scope_directory):
                return False

            if resolved.path in discovered_files:
                return resolved

            if path_exists(resolved.path):
                return resolved

        return None


def _resolve_module_path(import_str: str) -> Path | None:
    try:
        spec = importlib.util.find_spec(*import_str.rsplit(".", maxsplit=1))
    except (ModuleNotFoundError, ImportError):
        # Is bad import
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
) -> ResolvedFileImport | None:
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
