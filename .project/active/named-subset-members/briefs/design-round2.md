# Brief: design round 2, named-subset-members

Sent to the design session on 2026-10-26 after `design-review.md` (verdict Revise). Orchestrator decisions [AGENT]. The review's probe models are in `evidence/review-shapes/`.

Revise `design.md`, its plan and the prototype patch:

1. **M1: accept.** Track membership by slot (the root of a redefinition chain), so `rack : Rack { part :>> server_1 { ... } }` and dc3's `part :>> rack_1 { ... }` keep the member in its collection (25, not 20). Rerun the whole-corpus byte check with this change.
2. **M2: accept.** D6 uses the count the collection has after D4 (inherited), not only its own.
3. **S1: accept.** D7 decides from what the collection's declarations own, using the helper the prototype already has; remove the `KeyError` skip.
4. **S2: accept.** `OccurrenceIndex.children()` must not return a named member twice; check every other reader of the new slot filing the same way and list them.
5. **S3.** Record option A as `[AGENT] recommended, ratified by owner 2026-10-26`, and record the interpretation: a named subset with no count is one member, which matches modeller intent and dc3's 28 uses, though a literal reading of SysML Part 1 §7.6.3 would give it the collection's count. Accept an explicit `[1]` on a named member (its SysML meaning is exactly one member); keep refusing any other count.
6. **S4: accept.** The dc3 proof regenerates from the committed model tree (`git -C /home/reid/src/dc3 archive HEAD models`, package name `dc3_baseline`), since dc3's working tree has uncommitted edits from another session.
7. **S5: accept.** Apply the one count rule to a non-sibling member of a part with no count too, or refuse it by name; no extra copy.
8. **Minor:** merge refusal reasons where one reason covers the same rule; define "sibling" once.
9. Copy the review's product-lens block into `product-lens.md` with your dispositions; the lens gate must end DISPOSED.

Rerun the spec values, the review's failing probes and dc3 (committed tree) on the revised prototype. Don't change `src/`, don't commit. End with `ARTIFACT: <path>`.
