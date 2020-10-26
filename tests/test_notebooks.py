from __future__ import annotations

from pathlib import Path
from typing import Iterator

from git import Repo
from papermill import execute_notebook
from pytest import fixture


@fixture  # type: ignore
def notebook() -> Iterator[Path]:
    root = Path(
        Repo(".", search_parent_directories=True).working_tree_dir,
    ).joinpath("machine-learning")
    for path in root.glob("**/*.ipynb"):
        yield root.joinpath(path)


def test_notebooks(
    notebook_path: Path,
    tmp_path: Path,
) -> None:
    execute_notebook(
        str(notebook_path),
        str(tmp_path.joinpath(notebook_path.name)),
    )
