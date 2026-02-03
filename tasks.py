from collections.abc import Callable
from pathlib import Path
from typing import Any

from invoke import Collection, Context, task  # pyright: ignore[reportPrivateImportUsage]


##########################
# Version management tasks
@task
def set_version(c: Context, version: str):
    _run_multiple_tasks(
        c,
        (
            set_version_pyproject,
            set_version_python,
        ),
        version,
    )


@task
def set_version_pyproject(c: Context, version: str):
    print("Update version in pyproject.toml")
    c.run(f"uv version {version}")


@task
def set_version_python(_: Context, version: str):
    print("Update version in __version__.py")

    version_file_path = Path("./src/robotframework_find_unused/__version__.py")
    with version_file_path.open(mode="w") as f:
        f.write(f'__version__ = "{version}"\n')

    print(f"Replaced {version_file_path.as_posix()}")


#############
# Build tasks
@task
def build(c: Context):
    _run_multiple_tasks(
        c,
        (
            lint,
            test,
            build_source,
            build_gifs,
        ),
    )


@task
def build_source(c: Context):
    c.run("uv build")


@task
def build_gifs(c: Context):
    c.run("powershell ./docs/build/build-gifs.ps1")


##########
# QA tasks
@task
def lint(c: Context):
    c.run("uv run ruff check")


@task
def test(c: Context):
    c.run("uv run pytest -n auto")


#############
# Task config
ns = Collection(
    build,
    build_gifs,
    build_source,
    set_version,
    set_version_pyproject,
    set_version_python,
    lint,
    test,
)
ns.configure(
    {
        "run": {
            "echo": True,
            "echo_format": "> {command}",
        },
    },
)


#########
# Helpers
def _run_multiple_tasks(
    c: Context,
    tasks: tuple[Callable, ...],
    *args: Any,  # noqa: ANN401
    **kwargs: Any,  # noqa: ANN401
) -> None:
    print(f"Running {len(tasks)} tasks...")

    for t in tasks:
        print()
        print("--- task " + t.__name__ + " ---")
        print()

        try:
            t(c, *args, **kwargs)
        except Exception:
            print("FAILED task " + t.__name__)
            raise

    print()
    print("-" * 20)
    print()

    print(f"Ran {len(tasks)} tasks")
