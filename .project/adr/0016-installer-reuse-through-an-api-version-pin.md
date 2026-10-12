---
id: 0016
title: Reuse agentic-mbse's installer through an API version pin, not a package-version bound
date: 2026-10-12
owner: Reid W
status: active
amended_by: []
superseded_by: null
provenance: "[AGENT] (design premise conflict 1, DD4 and DD5; accepted by the orchestrator, 2026-10-12, amending spec L3-9)"
seams: [installer, agentic-mbse, fusion-tea]
supersedes: null
promoted_to: null
---

## Decision

`sysml-codegen install-commands` installs through agentic-mbse's `Installer`, on its own manifest, `.sysml-codegen/install.json`. The guarantee that the installed agentic-mbse has that API is an API version string, not a package-version bound: agentic-mbse exports `INSTALLER_API_VERSION = "installer/v1"`, and sysml-codegen pins it in `_upstream_pins.py`. `install-commands` checks it lazily, inside its own handler, and exits 1 naming the agentic-mbse revision needed when it is missing or different. The dependency bound stays `agentic-mbse>=0.1.3,<0.2`.

## Why

- **The producer gap.** agentic-mbse changes its API without changing its package version. It reported 0.1.3 both before and after its native installer landed, so no version bound can tell an installer-capable revision from an older one.
- Closing the gap with a version bump costs too much. The v6 snapshot loader refuses a snapshot whose recorded `agentic_mbse_version` differs from the running agentic-mbse (`snapshot/envelope.py`), so a bump makes every committed v6 snapshot unloadable.
- No consumer resolves agentic-mbse by version; every install is by git revision or path (design KB6). A string checked where the API is called is the guarantee that holds in that world.
- The check is lazy, so an older agentic-mbse breaks `install-commands` alone and never `generate`.
- Reusing the `Installer` keeps one implementation of the ownership rules: unmodified files refreshed, edits preserved or asked about, retired files pruned only inside the bundle.

## Invariants established

- Each installer reads and writes only its own manifest and prunes only under its own bundles, so `agentic-mbse init` and `install-commands` coexist in either order (design I5).
- `installer/v1` names the whole surface sysml-codegen calls: the constructor's keywords and the decide answers, `parents`, `write`, `save`, `actions` and its six keys, `install_bundle` and `frontmatter`. A shape change upstream changes the string, and `tests/conformance/test_upstream_pins.py` then fails here.
- The minimum agentic-mbse revision is named in `README.md` and in `cli/install.py`'s `INSTALLER_API_REVISION`, and `tests/unit/test_install_commands.py` holds the two equal.

## Rejected alternatives

- Bumping agentic-mbse to 0.1.4 with a raised bound was rejected: it makes every committed v6 snapshot unloadable.
- A standalone sysml-codegen installer was rejected: a second implementation of the ownership rules, free to drift.
- Subclassing `Installer` was rejected: it couples to internals the API string does not cover.
- A manifest shared with agentic-mbse was rejected: agentic-mbse's `init` would prune or claim the `run-study` bundle.
