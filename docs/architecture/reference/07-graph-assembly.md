# Exact Elaboration Architecture

The callable route is now source admission, strict elaboration into a validated `InstanceGraph`, and one-way projection into the route-neutral generation DTOs.

- Source admission and referent receipts: `snapshot/source_manifest.py`
- Identity, occurrence, value, equation, and physics semantics: `elaboration/`
- Projection and validation: `elaboration/project.py`
- Live orchestration: `orchestration/pipeline_builder.py`
- Strict v6 capture and load: `snapshot/capture.py` and `snapshot/envelope.py`
- Generation boundary: `generation/`

The Item 7 cutover tests under `tests/conformance/test_cutover_*.py` and the exact elaboration suites are the executable contract. Full post-cutover documentation and certification remain Item 8 work.
