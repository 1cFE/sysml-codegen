# expected-coverage.md — moved

**[OWNER 2026-08-13]** The coverage ledger moved to `tests/unit/data/expected-coverage.md`
as its durable home: it is the expected-value file of a live test
(`tests/unit/test_coverage_ledger_agreement.py`), and the suite's collection must not depend
on archive layout (it broke once, at the Item 3 archival — Item 4 audit F5). The content as
of this archive is unchanged by the move; its bytes at close remain in git history at this
path (`cec3f03..77b40f7`).
