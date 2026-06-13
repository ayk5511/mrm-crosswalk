# mrm-crosswalk

**A cross-jurisdiction crosswalk of machine-learning model-risk regulation, with an open compliance benchmark for quantitative finance.**

Machine-learning model-risk regulation in finance has fragmented across jurisdictions. This repository accompanies the paper *"A Cross-Jurisdiction Crosswalk of Machine-Learning Model-Risk Regulation, with an Open Compliance Benchmark for Quantitative Finance"* (Khan, 2026; SSRN) and provides two reusable artefacts:

1. **The crosswalk** ([`results/crosswalk.csv`](results/crosswalk.csv), CC-BY-4.0): twelve audit-trail / model-risk requirements mapped onto five binding regimes — **SR 11-7 / OCC 2011-12** (US), the **EU AI Act**, **PRA SS1/23** (UK), **MAS FEAT / Veritas** (Singapore), **OSFI E-23** (Canada) — and two voluntary frameworks (**NIST AI RMF**, **ISO/IEC 42001**), with the governing provision in each cell.

2. **The benchmark** (`mrm_crosswalk`, MIT): a reference scoring harness that scores a machine-learning pipeline against the union of those requirements, plus a seed [leaderboard](results/leaderboard.csv).

## The twelve requirements

Model inventory · replicable documentation · data provenance · versioning · independent validation · per-prediction logging · record retention · ongoing monitoring · governance · transparency · fairness · decommissioning.

Six are **mechanically checkable** from a repository (inventory, documentation+environment, data provenance, versioning, retention, decommissioning); the harness automates those six. The remaining six require code execution or manual review against the published codebook.

## Install & use

```bash
pip install -e .
# score any repository against the crosswalk:
mrm-crosswalk /path/to/some/ml-pipeline
# or:
python -m mrm_crosswalk.score /path/to/some/ml-pipeline
```

```python
from mrm_crosswalk import score_repository
s = score_repository("/path/to/repo")
print(s.summary())          # per-regime + union scores
print(s.union_score)        # fraction of the six checkable requirements met
```

## Seed leaderboard

`results/leaderboard.csv` is seeded with real harness output on public ML-finance pipelines (the author's own open-source repositories, as reproducible worked examples):

| Pipeline | Union (checkable) |
|---|---|
| `mr-audit` | 6/6 (100%) |
| `vol-eval` | 4/6 (67%) |
| `mrm-crosswalk` | 3/6 (50%) |

This is a **v0.1 seed**, intended to be extended — by adding regimes as columns, pipelines as rows, and updated provisions as the law changes — not as a finished ranking.

## Tests

```bash
PYTHONPATH=src python3 -m pytest tests/
```

## Honest scope

The crosswalk is an **interpretive reading of public regulatory text, not legal advice**; firms remain responsible for their own compliance determinations. It is **versioned** to the texts as of the dates recorded in the paper (SR 11-7 / OCC 2011-12 was revised in 2026; OSFI E-23 takes effect 2027). The harness automates six of the twelve requirements; the other six ship with a manual codebook.

## License & citation

Code: MIT (see [`LICENSE`](LICENSE)). The crosswalk data is released CC-BY-4.0. To cite, see [`CITATION.cff`](CITATION.cff) or the SSRN working paper.

## Trade-secret firewall

This repository contains only public methods, public regulatory sources, and original analysis. No proprietary content from any private work appears here.
