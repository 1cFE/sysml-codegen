| field | run1 | run2 | run3 | identical |
|---|---|---|---|---|
| env import-path gate | PASS | PASS | PASS | yes |
| env license key present | True | True | True | yes |
| env python | 3.12.11 | 3.12.11 | 3.12.11 | yes |
| env ruff / mypy / pytest | 0.16.2 / 2.3.0 / 9.1.1 | 0.16.2 / 2.3.0 / 9.1.1 | 0.16.2 / 2.3.0 / 9.1.1 | yes |
| env sysml_codegen | /home/reid/1cfe/sysml-codegen-item7-rebuild/src/sysml_codegen/__init__.py | /home/reid/1cfe/sysml-codegen-item7-rebuild/src/sysml_codegen/__init__.py | /home/reid/1cfe/sysml-codegen-item7-rebuild/src/sysml_codegen/__init__.py | yes |
| env agentic_mbse | /home/reid/1cfe/agentic-mbse-item7-rebuild/src/agentic_mbse/__init__.py | /home/reid/1cfe/agentic-mbse-item7-rebuild/src/agentic_mbse/__init__.py | /home/reid/1cfe/agentic-mbse-item7-rebuild/src/agentic_mbse/__init__.py | yes |
| env simkit | /home/reid/1cfe/teax/packages/teax-simkit/simkit/__init__.py | /home/reid/1cfe/teax/packages/teax-simkit/simkit/__init__.py | /home/reid/1cfe/teax/packages/teax-simkit/simkit/__init__.py | yes |
| HEAD codegen | 2819501178370db230acefdbcd02dfa15b409ac4 | 2819501178370db230acefdbcd02dfa15b409ac4 | 2819501178370db230acefdbcd02dfa15b409ac4 | yes |
| HEAD agentic | 6372ef7ba6ba4c869759fcf201c59aa128175c6f | 6372ef7ba6ba4c869759fcf201c59aa128175c6f | 6372ef7ba6ba4c869759fcf201c59aa128175c6f | yes |
| HEAD teax | 75eecb3bcf4baa0306107a96aa78b74ee667e970 | 75eecb3bcf4baa0306107a96aa78b74ee667e970 | 75eecb3bcf4baa0306107a96aa78b74ee667e970 | yes |
| codegen suite | 2086 passed, 34 skipped, 88 deselected | 2086 passed, 34 skipped, 88 deselected | 2086 passed, 34 skipped, 88 deselected | yes |
| codegen suite license-skip lines | 0 | 0 | 0 | yes |
| codegen suite rc | 0 | 0 | 0 | yes |
| exec lane | 88 passed | 88 passed | 88 passed | yes |
| corpus -k corpus | 9 passed, 2199 deselected | 9 passed, 2199 deselected | 9 passed, 2199 deselected | yes |
| capture_v6_batch --verify | 15 captured, 22 refused, 0 deviations | 15 captured, 22 refused, 0 deviations | 15 captured, 22 refused, 0 deviations | yes |
| batch non-timestamp fixture diff lines | 0 | 0 | 0 | yes |
| capture_v6_batch --check rc | 0 | 0 | 0 | yes |
| capture_v6_batch --check tail | 15 captured, 22 refused, 0 deviations | 15 captured, 22 refused, 0 deviations | 15 captured, 22 refused, 0 deviations | yes |
| ruff check src | Found 12 error | Found 12 error | Found 12 error | yes |
| ruff check src tests scripts | Found 642 error | Found 642 error | Found 642 error | yes |
| mypy src | Found 52 errors in 11 files | Found 52 errors in 11 files | Found 52 errors in 11 files | yes |
| agentic suite | 1831 passed, 1 skipped, 5 deselected | 1831 passed, 1 skipped, 5 deselected | 1831 passed, 1 skipped, 5 deselected | yes |
| agentic ruff check src | Found 1 error | Found 1 error | Found 1 error | yes |
| agentic ruff check tests | Found 120 error | Found 120 error | Found 120 error | yes |
| agentic mypy src | Found 108 errors in 26 files | Found 108 errors in 26 files | Found 108 errors in 26 files | yes |
| ledger paths | 304 rows checked, 0 problems | 304 rows checked, 0 problems | 304 rows checked, 0 problems | yes |
| ledger surface | 0 unrowed breakages | 0 unrowed breakages | 0 unrowed breakages | yes |
| ledger group 4B-G0 | affected=0 READY | affected=0 READY | affected=0 READY | yes |
| ledger group 4B-G1 | affected=0 READY | affected=0 READY | affected=0 READY | yes |
| ledger group 4B-G2 | affected=0 READY | affected=0 READY | affected=0 READY | yes |
| ledger group 4B-G3 | affected=0 READY | affected=0 READY | affected=0 READY | yes |
| ledger group 4B-G4 | affected=0 READY | affected=0 READY | affected=0 READY | yes |
| ledger group 4B-v5-family | affected=0 READY | affected=0 READY | affected=0 READY | yes |
| ledger replacements green | 223 | 223 | 223 | yes |
| ledger replacements not-required | 79 | 79 | 79 | yes |
| ledger replacements FAIL | 0 | 0 | 0 | yes |
| ledger replacements rc | 0 | 0 | 0 | yes |
| proof integrity | proof integrity: 0 problems over 0 blocked files | proof integrity: 0 problems over 0 blocked files | proof integrity: 0 problems over 0 blocked files | yes |
| doc distinctness | 31 numbered reference documents checked, 0 identical-content groups | 31 numbered reference documents checked, 0 identical-content groups | 31 numbered reference documents checked, 0 identical-content groups | yes |
| git diff --check codegen | rc=0 clean | rc=0 clean | rc=0 clean | yes |
| git diff --check agentic | rc=0 clean | rc=0 clean | rc=0 clean | yes |
| git status codegen | ## item7-rebuild \|  M .project/active/cutover-recovery/evidence/phase5-runs/build_candidate_final.py \| ?? .project/active/cutover-recovery/evidence/phase5-runs/final-runs/ | ## item7-rebuild \|  M .project/active/cutover-recovery/evidence/phase5-runs/build_candidate_final.py \| ?? .project/active/cutover-recovery/evidence/phase5-runs/final-runs/ | ## item7-rebuild \|  M .project/active/cutover-recovery/evidence/phase5-runs/build_candidate_final.py \| ?? .project/active/cutover-recovery/evidence/phase5-runs/final-runs/ | yes |
| git status agentic | ## item7-rebuild | ## item7-rebuild | ## item7-rebuild | yes |
| git status teax | ## constraint-semantics-item3 | ## constraint-semantics-item3 | ## constraint-semantics-item3 | yes |
| scale fusion_tea counts | {"attrs": 56, "calcs": 7, "constraints": 1, "entry_points": 27, "modules": 9, "occurrences": 8} | {"attrs": 56, "calcs": 7, "constraints": 1, "entry_points": 27, "modules": 9, "occurrences": 8} | {"attrs": 56, "calcs": 7, "constraints": 1, "entry_points": 27, "modules": 9, "occurrences": 8} | yes |
| scale fusion_tea envelope bytes | 112707 | 112707 | 112707 | yes |
| scale solar_battery_d5 counts | {"attrs": 350, "calcs": 77, "constraints": 0, "entry_points": 199, "modules": 77, "occurrences": 42} | {"attrs": 350, "calcs": 77, "constraints": 0, "entry_points": 199, "modules": 77, "occurrences": 42} | {"attrs": 350, "calcs": 77, "constraints": 0, "entry_points": 199, "modules": 77, "occurrences": 42} | yes |
| scale solar_battery_d5 envelope bytes | 1104468 | 1104468 | 1104468 | yes |
| scale catf_mfe_d5 counts | {"attrs": 376, "calcs": 42, "constraints": 9, "entry_points": 60, "modules": 43, "occurrences": 61} | {"attrs": 376, "calcs": 42, "constraints": 9, "entry_points": 60, "modules": 43, "occurrences": 61} | {"attrs": 376, "calcs": 42, "constraints": 9, "entry_points": 60, "modules": 43, "occurrences": 61} | yes |
| scale catf_mfe_d5 envelope bytes | 667339 | 667339 | 667339 | yes |

**51 / 51 fields identical across all three runs.**

### Step wall-clock (measurement, not an identity field)

| step | run1 s | run2 s | run3 s |
|---|---|---|---|
| env_gate | 0 | 0 | 0 |
| suite_codegen | 163 | 165 | 166 |
| suite_agentic | 15 | 15 | 15 |
| execution_lane | 16 | 15 | 16 |
| corpus_tests | 2 | 2 | 1 |
| batch_verify | 8 | 8 | 9 |
| batch_check | 0 | 0 | 0 |
| ruff_src | 1 | 0 | 0 |
| ruff_all | 0 | 0 | 0 |
| mypy_src | 0 | 0 | 0 |
| mb_ruff_src | 0 | 0 | 0 |
| mb_ruff_tests | 0 | 0 | 0 |
| mb_mypy_src | 0 | 1 | 0 |
| ledger_paths | 1 | 1 | 1 |
| ledger_surface | 0 | 0 | 1 |
| ledger_groups | 3 | 2 | 2 |
| ledger_replace | 695 | 694 | 694 |
| proof_integrity | 3 | 2 | 2 |
| doc_distinct | 0 | 0 | 0 |
| scale | 77 | 80 | 78 |
| diff_check_cg | 0 | 0 | 0 |
| diff_check_mb | 0 | 0 | 0 |
| status_cg | 0 | 0 | 0 |
| status_mb | 0 | 0 | 0 |
| status_teax | 0 | 0 | 0 |

### Scale timings and peak RSS (measurement, not an identity field)

| measurement | run1 | run2 | run3 |
|---|---|---|---|
| fusion_tea live_elaborate_s | 0.125–0.137 | 0.127–0.140 | 0.128–0.140 |
| fusion_tea project_s | 0.003–0.003 | 0.003–0.003 | 0.003–0.003 |
| fusion_tea capture_s | 0.174–0.176 | 0.180–0.183 | 0.183–0.191 |
| fusion_tea generate_live_s | 0.201–0.204 | 0.209–0.211 | 0.210–0.221 |
| fusion_tea generate_snapshot_s | 0.093–0.095 | 0.096–0.098 | 0.099–0.101 |
| fusion_tea peak_rss_mib | 222.5–243.9 | 222.2–244.1 | 222.3–243.1 |
| solar_battery_d5 live_elaborate_s | 0.398–0.406 | 0.412–0.423 | 0.429–0.438 |
| solar_battery_d5 project_s | 0.035–0.044 | 0.037–0.046 | 0.038–0.047 |
| solar_battery_d5 capture_s | 0.729–0.740 | 0.755–0.760 | 0.779–0.781 |
| solar_battery_d5 generate_live_s | 0.842–0.847 | 0.866–0.874 | 0.855–0.901 |
| solar_battery_d5 generate_snapshot_s | 0.632–0.644 | 0.650–0.679 | 0.645–0.686 |
| solar_battery_d5 peak_rss_mib | 267.6–280.9 | 278.2–292.5 | 270.3–290.6 |
| catf_mfe_d5 live_elaborate_s | 5.013–5.030 | 5.204–5.218 | 5.069–5.101 |
| catf_mfe_d5 project_s | 0.014–0.015 | 0.015–0.016 | 0.015–0.015 |
| catf_mfe_d5 capture_s | 5.198–5.214 | 5.382–5.408 | 5.222–5.290 |
| catf_mfe_d5 generate_live_s | 5.234–5.263 | 5.434–5.481 | 5.283–5.294 |
| catf_mfe_d5 generate_snapshot_s | 0.293–0.303 | 0.301–0.314 | 0.295–0.308 |
| catf_mfe_d5 peak_rss_mib | 304.7–321.0 | 324.3–347.1 | 311.7–339.4 |
