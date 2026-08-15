# Provenance — indexed `#(i)` source readiness fixture

Committed realization of the contract's SRC-02 family (coordinate 02a kin): a valid KerML
index-operator value expression (`plants#(1).plant_r`) used as a calculation source binding.
Derived from the Item-1 spike probe `form_bracket_hash.sysml` (throwaway, never committed);
this fixture gives the readiness coordinate a permanent test home.

- **Disposition:** UNSUPPORTED (D-8). Valid SysML, outside this executable subset. The
  diagnostic wording must say exactly that — never "invalid SysML".
- **Pre-Item-4 defect:** the chain parser silently dropped the `IndexExpression` first
  operand, so the binding degraded to a bare `plant_r` source path (02a
  CONTRADICTED_AT_HEAD). Item 4 Phase 1 retains the indexed form as immutable evidence
  (`SourceForm.INDEXED_SOURCE`) and screens it as `SI_INDEXED_SOURCE_UNSUPPORTED`.
- **Value-state nuance:** the published 02a key says occurrence `:>>` override; the cited
  AFT 4a probe (reproduced here) declares the value on the definition. The readiness
  outcome is value-state-invariant — the family ends before a runtime source exists. If
  Phase-5 acceptance mapping needs the override literally, add it there.
- Extraction-only by construction: generation from this form must fail closed, so no
  pipeline baseline or snapshot will ever be captured for it as a passing case.

Consumers: `tests/conformance/test_source_identity_extraction.py` (live readiness cases).
