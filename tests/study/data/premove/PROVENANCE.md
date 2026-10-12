# Provenance: pre-move study documents

These four files are copied byte for byte from fusion-tea at `b06585709`, from one committed study record: `exploration/stellarator_e2e/studies/20260916-primary-loop-sizing/`. They were written by the study tools before the tools moved to sysml-codegen, so their tool paths start with `scripts/study/`, or are `scripts/integrate.py`.

| File here | Source path in fusion-tea at `b06585709` | sha256 |
|---|---|---|
| `indicators.json` | `exploration/stellarator_e2e/studies/20260916-primary-loop-sizing/indicators.json` | `4f0661405df83e6fc691b4c3fd9fee979b848bda49c3f5b511321e423e166972` |
| `preflight_results.json` | `exploration/stellarator_e2e/studies/20260916-primary-loop-sizing/results/preflight_results.json` | `f74d099d3a022307a73f34ead4f03373e1ffc1d5ca912c3bc15538315c1827d8` |
| `verification_summary.json` | `exploration/stellarator_e2e/studies/20260916-primary-loop-sizing/results/verification_summary.json` | `2743773729503d1f8bd3b03c8ba44ea564689414f7c58333132d25be2cc34361` |
| `integration-return.json` | `exploration/stellarator_e2e/studies/20260916-primary-loop-sizing/preparation/integration-return.json` | `a34ee542cad372634810f289bfd17be435f88e6f076c009bf40b88bc97aeb926` |

`tests/study/test_tool_identity.py` validates the first three against the unchanged schemas and checks that every tool path keeps its pre-move prefix: a committed record stays valid as written (spec SC7, D7). The integration return has no shipped schema, so it gets the prefix check only.

Never edit these files. A changed byte makes them something fusion-tea never wrote.
