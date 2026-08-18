# P-003 — No workarounds to accept bad models

**Status:** Standing product rule
**Filed:** 2026-08-16, self-binding-replacement (post-audit session)
**Grade:** `[OWNER-VERBATIM, 2026-08-16]`
**Source:** owner instruction in the 2026-08-16 self-binding-replacement working session, given
while ruling on the F-4 definition-owned sideways-reach behavior

---

## The promise — **[OWNER-VERBATIM, 2026-08-16]**

> we do NOT create workarounds to accept bad models -- we follow what KerML, SysMLv2 and SysIDE
> support

Reproduced exactly. This is the owner-originated core of this entry; it survives verbatim under
capture-fidelity law 2 and nothing below rewrites it.

Owner context from the same session, same grade:

> we are ... wasting so much ... time chasing bullshit -- trying to support things that aren't
> supported by the standard or the parser. this was the root cause of all the ... slop we've had.

---

## What it binds

When authored model text has no defined meaning under KerML, SysML v2, or SysIDE's resolution,
the product **refuses with a diagnostic**. It does not invent resolution behavior — no positional
searches, no "find the one plausible instance," no silent defaults — to make an ill-formed model
generate. A refused model is the correct outcome for an ill-formed model.

This is the product-level generalization of rules the codebase already enforces piecewise: D-4
(a self-binding is never reinterpreted as an outer reference), the exact-owner anchoring of
[P-002](P-002-exact-owner-anchoring.md), and the `SI_*` readiness refusals.

## First application

The definition-owned lineage-miss fallback (spike F-4 family): KerML makes that configuration
ill-formed (`checkConnectorTypeFeaturing`, KerML §8.3.4:5807; Part 1 §8.4.1 — a model violating a
semantic constraint has no defined semantics), so the resolver's descendant/sibling occurrence
search is a workaround this promise forbids. Removal is owned by `[DEF-OWNED-SIDEWAYS-REACH]`
(`.project/backlog/BACKLOG.md`). After transition A3, **every** definition-owned lineage miss is
final and refuses with `SI_OCCURRENCE_MISSING`; the resolver never searches descendants or siblings
for a substitute. Exact usage-owner anchoring, local definition-owned lineage mapping, bare
references, and explicit occurrence paths remain unchanged. This agent-written application status
describes the Phase 4 production candidate; independent audit is still pending. The
owner-verbatim promise above is unchanged.
