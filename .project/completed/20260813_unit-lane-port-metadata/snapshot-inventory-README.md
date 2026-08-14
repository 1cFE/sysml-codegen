# Pointer stub — inventory JSONs moved

`snapshot-inventory-pre.json` and `snapshot-inventory-final.json` moved (bytes unchanged) to
`tests/unit/data/item8-snapshot-inventory-{pre,final}.json` on 2026-08-13, after this item's
archival broke `tests/conformance/test_v6_snapshot_inventory.py` (7 failures: the test read the
`.project/active/` path). Same fix family as Item 4's F5 ruling **[OWNER 2026-08-13]**: suite
collection must not depend on archive layout; the durable home is `tests/unit/data/`. Move
performed by the Item 9 orchestrator; recorded in Item 9's verification.md as a rider.
