"""Audit script for Paper 6 (regulatory crosswalk + open compliance benchmark).

Re-derives the structural claims of the paper from the machine-readable
crosswalk artefact in results/crosswalk.csv. Must print
``ALL CHECKS PASSED`` (exit 0) before the paper is considered ship-ready.

Usage:
    python3 paper/audit.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

SHARED = Path(__file__).resolve().parent.parent.parent.parent / "shared" / "lib"
sys.path.insert(0, str(SHARED))
from audit_helpers import Auditor  # type: ignore

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    audit = Auditor()
    cw = REPO_ROOT / "results" / "crosswalk.csv"

    audit.section("CROSSWALK ARTEFACT")
    audit.file_exists(path=cw)
    with open(cw) as f:
        rows = list(csv.DictReader(f))
    cols = list(rows[0].keys()) if rows else []
    audit.check_equal(actual=len(rows), expected=12, label="crosswalk requirement rows")
    audit.check_equal(actual=len(cols), expected=7,
                      label="crosswalk columns (requirement + 6 regime columns)")
    expected_regimes = {
        "sr_11_7_us", "eu_ai_act", "pra_ss1_23_uk",
        "mas_feat_veritas_sg", "osfi_e23_ca", "nist_iso",
    }
    audit.check_equal(actual=set(cols) - {"requirement"}, expected=expected_regimes,
                      label="regime columns")

    audit.section("DIVERGENCE CLAIMS (text must match the artefact)")
    by_req = {r["requirement"]: r for r in rows}
    retention = by_req["Record retention (duration)"]
    audit.check_equal(actual="6 months" in retention["eu_ai_act"], expected=True,
                      label="EU AI Act sets the >=6-month retention floor (row 7)")
    audit.check_equal(actual=retention["sr_11_7_us"], expected="--",
                      label="SR 11-7 has no fixed retention floor (row 7)")
    fairness = by_req["Fairness / bias assessment"]
    audit.check_equal(actual=fairness["sr_11_7_us"], expected="--",
                      label="SR 11-7 has no explicit fairness requirement (row 11)")
    audit.check_equal(actual="Fairness" in fairness["mas_feat_veritas_sg"], expected=True,
                      label="MAS FEAT carries the fairness requirement (row 11)")
    decom = by_req["Decommissioning / lifecycle end"]
    audit.check_equal(actual="Explicit" in decom["osfi_e23_ca"], expected=True,
                      label="OSFI E-23 makes decommissioning explicit (row 12)")

    audit.section("PROSE CONSISTENCY")
    tex = "".join(p.read_text() for p in sorted((REPO_ROOT / "paper" / "sections").glob("*.tex")))
    tex += (REPO_ROOT / "paper" / "main.tex").read_text()
    audit.check_equal(actual="twelve" in tex.lower(), expected=True,
                      label="paper states 'twelve' requirements")
    audit.check_equal(actual="five binding regimes" in tex, expected=True,
                      label="paper states 'five binding regimes'")

    return audit.finish()


if __name__ == "__main__":
    sys.exit(main())
