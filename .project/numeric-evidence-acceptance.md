# Numeric evidence acceptance

[OWNER] Fix the blank study column problem across affected repositories, on new branches from main, and submit PRs (2026-09-05 request in fusion-tea).

[INHERITED: fusion-tea `.project/research/20260905-091948_blank-study-column-root-cause.md`] Generated multi-output fields already reach separate numeric pipeline exits. TEAx evidence projection drops their plain numbers.

[AGENT] Keep generated representations unchanged. Add a real-runtime acceptance test generating and sealing a two-output calculation and a dependent single-output calculation through live and snapshot routes. Assert explicit, distinct expected values at evaluation and after study-store close/reopen/query, before and after changing an input. Remove the mutation test's obsolete multi-output evidence exclusion and assert coverage of the entire graph's numeric outputs.

[AGENT] This acceptance requires TEAx's numeric publication repair (evidence schema v3). No production codegen dependency pin or package regeneration is required by this test-only change. Historic stores retain their prior evidence; new runtime schema compatibility prevents mixing old and new study evidence.
