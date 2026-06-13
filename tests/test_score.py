"""Tests for the mrm-crosswalk scoring harness."""
from __future__ import annotations

import subprocess
import sys

from mrm_crosswalk import (
    CHECKABLE,
    REGIME_COLUMNS,
    load_crosswalk,
    score_repository,
)


def test_crosswalk_loads_twelve_requirements():
    rows = load_crosswalk()
    assert len(rows) == 12
    # requirement column + 6 regime columns
    assert set(REGIME_COLUMNS).issubset(rows[0].keys())
    assert "requirement" in rows[0]


def test_checkable_set_is_six():
    assert CHECKABLE == {1, 2, 3, 4, 7, 12}
    assert len(CHECKABLE) == 6


def _make_compliant_repo(root):
    (root / "README.md").write_text("# Project\nData availability: see data/.\n")
    (root / "requirements.txt").write_text("numpy\n")
    (root / "MODEL_CARD.md").write_text("# Model Card\n")
    (root / "data").mkdir()
    (root / "data" / ".gitkeep").write_text("")
    (root / ".git").mkdir()
    (root / "RETENTION.md").write_text("Logs are retained for at least six months.\n")
    (root / "DECOMMISSION.md").write_text("Model decommissioning procedure.\n")


def test_fully_compliant_repo_scores_all_checkable_met(tmp_path):
    _make_compliant_repo(tmp_path)
    s = score_repository(tmp_path)
    assert s.union_checkable_met == 6
    assert s.union_score == 1.0
    for i in CHECKABLE:
        assert s.per_requirement[i]["status"] == "met", i


def test_empty_repo_scores_zero(tmp_path):
    s = score_repository(tmp_path)
    assert s.union_checkable_met == 0
    assert s.union_score == 0.0


def test_manual_requirements_flagged(tmp_path):
    s = score_repository(tmp_path)
    manual = [i for i, v in s.per_requirement.items() if not v["checkable"]]
    assert set(manual) == {5, 6, 8, 9, 10, 11}
    for i in manual:
        assert s.per_requirement[i]["status"] == "manual"


def test_per_regime_scores_present(tmp_path):
    _make_compliant_repo(tmp_path)
    s = score_repository(tmp_path)
    # EU AI Act is the only regime with a retention requirement (row 7);
    # a compliant repo should score it among its applicable checkable set.
    assert s.per_regime["eu_ai_act"]["score"] == 1.0
    # every regime reports a numeric or None score
    for c in REGIME_COLUMNS:
        sc = s.per_regime[c]["score"]
        assert sc is None or 0.0 <= sc <= 1.0


def test_partial_documentation(tmp_path):
    (tmp_path / "README.md").write_text("# Only a readme, no env file\n")
    s = score_repository(tmp_path)
    assert s.per_requirement[2]["status"] == "partial"


def test_cli_runs(tmp_path):
    _make_compliant_repo(tmp_path)
    out = subprocess.run(
        [sys.executable, "-m", "mrm_crosswalk.score", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert out.returncode == 0
    assert "union (checkable): 6/6" in out.stdout
