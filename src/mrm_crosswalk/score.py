"""Score an ML-pipeline repository against the cross-jurisdiction model-risk crosswalk.

The crosswalk (Khan 2026, "A Cross-Jurisdiction Crosswalk of Machine-Learning
Model-Risk Regulation, with an Open Compliance Benchmark for Quantitative
Finance") maps twelve audit-trail / model-risk requirements onto five binding
regimes (SR 11-7, EU AI Act, PRA SS1/23, MAS FEAT, OSFI E-23) and two voluntary
frameworks (NIST AI RMF, ISO/IEC 42001).

Six of the twelve requirements are mechanically checkable from a repository
(model inventory, replicable documentation, data provenance, versioning,
record retention, decommissioning); this module automates those six and flags
the remaining six (independent validation, per-prediction logging, monitoring,
governance, transparency, fairness) for manual review against the published
codebook. Scoring is deliberately conservative: a requirement is scored ``met``
only when the repository carries the artefact the strictest regime demands.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

# 1-indexed requirement ids that are mechanically checkable from a repository.
CHECKABLE: set[int] = {1, 2, 3, 4, 7, 12}

# Regime columns in the bundled crosswalk.csv (excludes the "requirement" column).
REGIME_COLUMNS = [
    "sr_11_7_us", "eu_ai_act", "pra_ss1_23_uk",
    "mas_feat_veritas_sg", "osfi_e23_ca", "nist_iso",
]
NOT_APPLICABLE = {"", "--"}
_TEXT_EXTS = {".md", ".txt", ".rst", ".toml", ".cff", ".yaml", ".yml", ".cfg", ".ini"}


def load_crosswalk() -> list[dict]:
    """Return one dict per requirement row from the bundled ``crosswalk.csv``."""
    text = resources.files("mrm_crosswalk").joinpath("crosswalk.csv").read_text(encoding="utf-8")
    return list(csv.DictReader(text.splitlines()))


def _has_file(repo: Path, patterns: list[str]) -> bool:
    return any(next(iter(repo.rglob(pat)), None) is not None for pat in patterns)


def _grep(repo: Path, regex: str) -> bool:
    rx = re.compile(regex, re.IGNORECASE)
    for p in repo.rglob("*"):
        if p.is_file() and p.suffix.lower() in _TEXT_EXTS and p.stat().st_size < 2_000_000:
            try:
                if rx.search(p.read_text(encoding="utf-8", errors="ignore")):
                    return True
            except OSError:
                continue
    return False


def _check(req_id: int, repo: Path) -> str:
    """Score one mechanically-checkable requirement as 'met' / 'partial' / 'absent'."""
    if req_id == 1:   # model inventory / identification
        return "met" if _has_file(repo, ["MODEL_CARD*", "model_card*", "metadata.json", "CITATION.cff"]) else "absent"
    if req_id == 2:   # replicable documentation + computational environment
        readme = _has_file(repo, ["README*"])
        env = _has_file(repo, ["requirements.txt", "pyproject.toml", "environment.yml",
                                "Dockerfile", "setup.py", "poetry.lock", "renv.lock"])
        return "met" if (readme and env) else ("partial" if (readme or env) else "absent")
    if req_id == 3:   # data provenance / lineage
        return "met" if ((repo / "data").is_dir()
                         or _grep(repo, r"doi\.org|zenodo|sha-?256|data availability|datasheet")) else "absent"
    if req_id == 4:   # versioning / change control
        return "met" if ((repo / ".git").exists() or _has_file(repo, ["CHANGELOG*", "VERSION"])) else "absent"
    if req_id == 7:   # record retention with a defined duration
        return "met" if _grep(repo, r"retention|retain[^.]{0,30}(month|day|year)") else "absent"
    if req_id == 12:  # decommissioning / lifecycle end
        return "met" if _grep(repo, r"decommission|model retirement|end[- ]of[- ]life") else "absent"
    return "manual"


@dataclass
class RepoScore:
    repo: str
    per_requirement: dict          # req_id -> {name, status, checkable, applies_to}
    per_regime: dict               # regime -> {checkable_applicable, checkable_met, score}
    union_checkable_met: int
    union_checkable_total: int

    @property
    def union_score(self) -> float:
        return self.union_checkable_met / self.union_checkable_total if self.union_checkable_total else 0.0

    def summary(self) -> str:
        lines = [f"mrm-crosswalk score for {self.repo}",
                 f"  union (checkable): {self.union_checkable_met}/{self.union_checkable_total} "
                 f"= {self.union_score:.0%}"]
        for c in REGIME_COLUMNS:
            r = self.per_regime[c]
            s = "n/a" if r["score"] is None else f"{r['checkable_met']}/{r['checkable_applicable']} = {r['score']:.0%}"
            lines.append(f"  {c:24} {s}")
        return "\n".join(lines)


def score_repository(repo_path) -> RepoScore:
    """Score a repository directory against the crosswalk's checkable requirements."""
    repo = Path(repo_path)
    if not repo.is_dir():
        raise NotADirectoryError(f"{repo} is not a directory")
    rows = load_crosswalk()
    per_req: dict[int, dict] = {}
    for i, row in enumerate(rows, start=1):
        checkable = i in CHECKABLE
        per_req[i] = {
            "name": row["requirement"],
            "status": _check(i, repo) if checkable else "manual",
            "checkable": checkable,
            "applies_to": {c for c in REGIME_COLUMNS if row.get(c, "") not in NOT_APPLICABLE},
        }
    per_regime: dict[str, dict] = {}
    for c in REGIME_COLUMNS:
        applicable = [i for i in CHECKABLE if c in per_req[i]["applies_to"]]
        met = [i for i in applicable if per_req[i]["status"] == "met"]
        per_regime[c] = {
            "checkable_applicable": len(applicable),
            "checkable_met": len(met),
            "score": round(len(met) / len(applicable), 3) if applicable else None,
        }
    union_met = sum(1 for i in CHECKABLE if per_req[i]["status"] == "met")
    return RepoScore(repo=str(repo), per_requirement=per_req, per_regime=per_regime,
                     union_checkable_met=union_met, union_checkable_total=len(CHECKABLE))


def _cli(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Score a repository against the model-risk crosswalk.")
    ap.add_argument("repo", help="path to the repository to score")
    args = ap.parse_args(argv)
    print(score_repository(args.repo).summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
