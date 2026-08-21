---
id: 0001
title: Route decisions by who they bind
date: 2026-08-21
owner: Reid W
status: active
amended_by: []
superseded_by: null
provenance: "[OWNER]"
seams: [project-workflow, documentation]
supersedes: null
promoted_to: null
---

## Decision

Ask one question when filing a decision: **Who is bound by this decision — the person writing the
system's inputs, or the person changing the system itself?** An input-author-facing decision stays
with the system's input-authoring documentation; a system-builder-facing decision goes in the
system's decision register.

## Why

The audience that must obey a decision is stable across repositories and systems. A list of
repo-specific subjects is not. Keeping input-authoring decisions beside the inputs they constrain
also puts the rule where an author needs it, while the system register remains the place a builder
checks before changing implementation.

## Invariants established

- Route by the audience the decision binds, not by its topic, component, or files changed.
- File one ruling in one register. Other documents cite it rather than duplicate it.

## Rejected alternatives

- A single decision register was rejected because it detaches input-authoring rules from the
  documentation an input author reads.
- A subject-by-subject routing list was rejected because it would not generalize beyond this repo.
