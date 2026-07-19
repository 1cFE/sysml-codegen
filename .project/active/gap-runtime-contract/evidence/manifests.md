# Generated Tree Manifest Summary

- Shared input manifest: `5ce74869c17d8f5699970d7494c23fa585fc2ad5698e6ad2ca6d38dfe1bdefb5`.
- Baseline snapshot tree before behavior execution:
  `ca9be991e98b448dfc9ca05b82df527decbbdbf98113f87c594e6e07736a5058`.
- Candidate snapshot tree before behavior execution:
  `d218674469279b2a45525a4c62cee75abdf5dc6e85656adb205528ad83347263`.
- Before/after classifier changed exactly:
  `modules/plantvaluesdesign/plantviabilityconstraintmodule.py` (approved sentence only) and
  `contracts/package_contract.json` (derived seal). `unapproved` was empty.
- Candidate live versus snapshot classifier ran before behavior execution with `changed: []` and
  `unapproved: []` across the complete file trees.
- The fresh-process behavior runner then changed copied generated input files to exercise the
  non-finite case and wrote run artifacts. Post-behavior aggregate hashes therefore are not route
  parity evidence.
