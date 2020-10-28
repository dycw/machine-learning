from __future__ import annotations

from numpy import concatenate
from pandas import DataFrame
from sklearn.datasets import make_blobs


def generate_data(random_state: int = 1) -> DataFrame:
    X, y = make_blobs(centers=3, cluster_std=3.0, random_state=random_state)
    return DataFrame(
        concatenate([X, y.reshape(-1, 1)], axis=1),
        columns=["x_1", "x_2", "y"],
    ).astype({"y": int})
