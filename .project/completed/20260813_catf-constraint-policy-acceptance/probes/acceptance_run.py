"""Item 5 Phase 6. The derivative through the real TEAx lane, twice, into durable storage.

One generated package, two candidates, two runs, both persisted and queried back:

- **gate-infeasible** — the model's own **authored** design point. Under finding 6-D this is
  the *rejected* candidate: the magnet cryoplant draws 5.43x the plant's gross electric output,
  so net power is negative before any mutation. Basis: `../cryo_derivation.py`.
- **gate-feasible** — `p_fusion = 20000`, a **machinery exemplar, not a recommended design**.
  It exists only to show the satisfied path executes.

**The mutation is injected at runtime, not written into `inputs/*.json`.** D6 said the mutation
"lives in the generated inputs/*.json". That route is refused by the product: the package
contract covers the on-disk bytes, so editing a sealed input breaks the seal, and
`test_editing_a_sealed_input_and_resealing_is_refused` pins that refusal in code. The supported
route — the one Item 3's mutation lane already uses — is TEAx's typed entry injection.
D6's intent is preserved exactly: one package, two input sets, the mutation a physics input
value rather than a model edit or a study-config override. The seal stays an active check
throughout, because the same loader verifies the package the evaluator runs.

Run: probes/licensed.sh acceptance_run.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path("/home/reid/1cfe/sysml-codegen-item7-rebuild")
sys.path.insert(0, str(REPO))

from tests.execution.real_teax import package_loader  # noqa: E402

PACKAGE = Path("/tmp/item5acc/route2_inplace")
NAME = "catf_gated"
ROOT = Path("/tmp/item5acc/acceptance")

P_FUSION = "CATFMFEPhysics__catf_physics__p_fusion"
A2 = "CATFMFEPhysics__catf_physics__net_power_viable__d8cad14493e47fbd"
A3 = "CATFMFEPhysics__catf_physics__parasitic_fraction_ok__280b94b2e8d184f5"

CANDIDATES = (
    ("gate_infeasible_authored", {}, "the authored design point (p_fusion = 2600.0)"),
    ("gate_feasible_exemplar", {P_FUSION: 20000.0}, "machinery exemplar, NOT a design"),
)


def disposition_for(headline: str) -> str:
    """The disposition `ObjectivePolicy` gives this headline at default configuration."""
    from simkit.study.policy import _disposition_for, _HEADLINE_DISPOSITION

    if headline == "satisfied":
        return "feed-strategy"
    return _disposition_for(headline, _HEADLINE_DISPOSITION, "_HEADLINE_DISPOSITION")


def main() -> None:
    from simkit.evaluation.evaluator import PreparedEvaluator
    from simkit.evaluation.evidence import canonical_headline
    from simkit.study.bridge import CandidateBridge
    from simkit.study.policy import _coverage_of

    ROOT.mkdir(parents=True, exist_ok=True)
    loader = package_loader(PACKAGE, NAME, ROOT / "link")
    evaluator = PreparedEvaluator(
        loader, PACKAGE / "pipelines" / "pipeline.yaml", expects_constraint_report=True
    )
    bridge = CandidateBridge(evaluator.entry_models)

    records = {}
    for candidate_id, overrides, label in CANDIDATES:
        evidence = evaluator.evaluate(bridge.build(overrides))
        report = evidence.report
        headline = evidence.responses["headline"]
        canonical = canonical_headline(report["headline"])
        coverage = _coverage_of(evidence)
        record = {
            "candidate_id": candidate_id,
            "label": label,
            "overrides": overrides,
            "report_headline": report["headline"],
            "runtime_headline": headline,
            "canonical_token": canonical,
            "policy_disposition": disposition_for(canonical),
            "verdicts": {
                "A2 net_power_viable": evidence.responses.get(A2),
                "A3 parasitic_fraction_ok": evidence.responses.get(A3),
            },
            "coverage": coverage.get("coverage"),
            "catalog_fingerprint": coverage.get("catalog_fingerprint"),
            "executable_fingerprint": evidence.provenance.executable_fingerprint,
            "p_electric_gross": evidence.outputs.get(
                "CATFMFEPhysics__catf_physics__gross_electric__p_electric_gross"
            ),
            "cryo_cooling_power": evidence.outputs.get(
                "CATFMFEMagnets__catf_tf_system__cryo_load__cooling_power"
            ),
        }
        records[candidate_id] = record
        print(f"\n=== {candidate_id} — {label}")
        print(json.dumps(record, indent=2, sort_keys=True, default=str))

    out = ROOT / "case_records.json"
    out.write_text(json.dumps(records, indent=2, sort_keys=True, default=str) + "\n")
    print(f"\nwrote {out}")

    # Both candidates must persist BOTH a verdict and a coverage account — the Item 3
    # contract that a study query answers "how covered was this candidate" off the row.
    for candidate_id, record in records.items():
        assert record["coverage"] is not None, f"{candidate_id}: no coverage on the record"
        assert record["verdicts"]["A2 net_power_viable"], f"{candidate_id}: no A2 verdict"
        assert record["verdicts"]["A3 parasitic_fraction_ok"], f"{candidate_id}: no A3 verdict"
        assert record["catalog_fingerprint"], f"{candidate_id}: no catalog fingerprint"
    print("\nBOTH candidates persist a verdict AND a coverage account.")

    assert records["gate_infeasible_authored"]["policy_disposition"] == "reject"
    assert records["gate_feasible_exemplar"]["policy_disposition"] == "feed-strategy"
    print("policy: authored -> reject ; exemplar -> feed-strategy")


if __name__ == "__main__":
    main()
