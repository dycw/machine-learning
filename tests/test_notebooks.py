from __future__ import annotations

from pathlib import Path
from typing import Iterator

from git import Repo
from papermill import execute_notebook
from pytest import mark


def _yield_notebook_paths() -> Iterator[Path]:
    root = Path(Repo(".", search_parent_directories=True).working_tree_dir)
    for path in root.glob("**/*.ipynb"):
        if not any(p == ".ipynb_checkpoints" for p in path.parts):
            yield root.joinpath(path)


@mark.parametrize(  # type: ignore
    "notebook_path",
    list(_yield_notebook_paths()),
    ids=str,
)
def test_notebooks(notebook_path: Path, tmp_path: Path) -> None:
    execute_notebook(
        str(notebook_path),
        str(tmp_path.joinpath(notebook_path.name)),
    )
