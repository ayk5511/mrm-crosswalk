"""mrm-crosswalk: a cross-jurisdiction model-risk crosswalk and an open
compliance benchmark for machine-learning pipelines in finance.

See Khan (2026), "A Cross-Jurisdiction Crosswalk of Machine-Learning Model-Risk
Regulation, with an Open Compliance Benchmark for Quantitative Finance."
"""
from __future__ import annotations

from .score import (
    CHECKABLE,
    REGIME_COLUMNS,
    RepoScore,
    load_crosswalk,
    score_repository,
)

__version__ = "0.1.0"
__all__ = [
    "CHECKABLE",
    "REGIME_COLUMNS",
    "RepoScore",
    "load_crosswalk",
    "score_repository",
    "__version__",
]
