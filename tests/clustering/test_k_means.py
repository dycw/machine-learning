from __future__ import annotations

from pandas import DataFrame

from machine_learning.clustering.k_means import generate_data


def test_generate_data() -> None:
    df = generate_data()
    assert isinstance(df, DataFrame)
    assert list(df.columns) == ["x_1", "x_2", "y"]
    assert df.x_1.dtype == float
    assert df.x_2.dtype == float
    assert df.y.dtype == int
