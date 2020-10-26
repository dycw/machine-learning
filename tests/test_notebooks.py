from __future__ import annotations

from pathlib import Path
from typing import Iterator

from git import Repo
from pytest import mark
from pytest_notebook.nb_regression import NBRegressionFixture


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
def test_notebooks(
    nb_regression: NBRegressionFixture,
    notebook_path: Path,
) -> None:
    nb_regression.check(str(notebook_path), raise_errors=True)
