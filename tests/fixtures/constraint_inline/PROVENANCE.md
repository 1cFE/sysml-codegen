# Provenance

New fixture for CONSTRAINT-EXEC Item 5 (design.md D6, Appendix B). Proves the
source-form axis: an assertion whose predicate is inline on the usage itself
(`ConstraintSource.form == "inline"`), not typed by a named `constraint def`
(the `definition_typed` form S4 exclusively exercised). `value > 0.0` is written
directly on the `assert constraint positive { ... }` usage with no
`: 'Constraint Def'` typing clause, so `constraint.result_expression` is
populated directly and `_classify()` (agentic-mbse `constraint_extraction.py`)
resolves `form="inline"`.
