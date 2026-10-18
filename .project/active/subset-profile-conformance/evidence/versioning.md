# Versioning evidence (Step 1.5, criterion A2, design D12)

**Result.** No package version identifies the subset contract. `SUBSET_PROFILE_VERSION` does. agentic-mbse stays at 0.1.3, and sysml-codegen's requirement stays `agentic-mbse>=0.1.3,<0.2` (`pyproject.toml:24`). The contract is identified by `subset-profile/v1`, which sysml-codegen now pins as `SUBSET_PROFILE_VERSION` in `src/sysml_codegen/_upstream_pins.py`. `src/sysml_codegen/subset_profile_adapter.py` refuses to import when the installed screen reports a different value.

**Which version first carries it.** No package version does. `SUBSET_PROFILE_VERSION` first appears in agentic-mbse `b2d5768d` (Item 1 Phase 5, merged in PR #30 as `ccd57d83`). Its parent `b2d5768d~1` has no `SUBSET_PROFILE_VERSION`, and both report `version = "0.1.3"`. So 0.1.3 names revisions with and without the contract, and the package requirement cannot exclude the ones without it. The criterion is met in D12's form: the pin, checked when the adapter is imported, is what excludes them.

## How it was checked

- **Package version before and after.** `version = "0.1.3"` in agentic-mbse's `pyproject.toml` at the 2a base `ccd57d83` and at `186d7ff3` (the P1.4 commit, the branch head before P1.5). `git log ccd57d83..HEAD -- pyproject.toml src/agentic_mbse/__init__.py` is empty: no 2a commit touches either file.
- **Installed version.** In sysml-codegen's environment, `agentic_mbse.__version__` is `0.1.3`, loaded from `/home/reid/src/subset-conformance/agentic-mbse/src/agentic_mbse/__init__.py` (the editable install of the 2a worktree).
- **Contract version before and after.** `SUBSET_PROFILE_VERSION = "subset-profile/v1"` in `src/agentic_mbse/sysml/subset_profile.py` at `ccd57d83` and at `186d7ff3`; the installed module reports the same value. The pin test in `tests/conformance/test_upstream_pins.py` checks the pin against the installed value.
- **Tags.** `git tag --list 'v*'` in agentic-mbse returns nothing. The only tags are `archive/...` and `stop-parser/agentic-final`; none is a release tag.

## Not checked

- The package index. Nothing in 2a publishes (D12), and no index was queried.
- The `v1` → `v2` bump. D12 makes it one bump covering all of 2a's record changes; it lands with those changes in a later phase, not here.
