# Product-Lens — scaffolding-register-boundary

Append-only. One block per run.

**Epic: REPO-CLEANUP** (`.project/backlog/epic_repo_cleanup.md`). Gates resolve against the epic's
live gate, not against this copy.

Epic findings that reach this item, at their original source grades:

- `epic_plan-F6` (agent/ratified via `P-002`) — the `allow_nan=False` fix at
  `contracts/serialize.py` and the V11 doc corrections were briefly moved from Item 8 into this
  item. `[OWNER, 2026-08-20]` removed them from the epic entirely: neither belongs to a scaffolding
  item. Both now ride as standalone `[SERIALIZE-NAN-SEAL]` and `[V11-DEAD-GATE-DOCS]` at the top of
  `.project/backlog/BACKLOG.md`, carrying the widened scope that `spec-F3` and `spec-F4` found.
  The lens's underlying concern — that neither be stranded behind a five-day epic — is satisfied
  more strongly by unbundling than by relocation.
- `epic_plan-F1` (owner/HARD core in `P-001`; agent/ratified in `P-002`) — product-ledger citations
  must resolve after the Item 5 purge. Reaches this item because the rename this item performs is
  the first thing that can break them. See `spec-F5`.

---

## Run 1 — spec stage, 2026-08-20

Gate: **DISPOSED** (spec-F1 … spec-F6). Smell 7 fired and is disposed with spec-F2.

All six findings were verified against the code and files before disposition:

- `spec-F1` confirmed — no promise entry has YAML frontmatter; all four open with `# P-00N — …`.
- `spec-F3` confirmed — `write_contract_json` (`contracts/serialize.py:34`) also omits
  `allow_nan=False`, and it writes the file `PackageContract` hashes.
- `spec-F4` confirmed — `docs/architecture/overview.md:63,141` and
  `docs/architecture/modeling-assumptions.md:750-785` still assert V11 fires.
- `spec-F5` confirmed — `P-001:114` cites `modeling-assumptions.md:588` (ADR-009), the entry this
  item may re-home; and a mechanical sweep found 13 live `P-00N` citation sites, not the 4 the
  first draft listed.

```
## spec — 2026-08-20 — rev da15f14 (.project/active/scaffolding-register-boundary/spec.md)
Point (re-derived): The owner's stated promises are payload — P-003 and P-004 survive verbatim, at the owner's emphasis, and stay reachable from the ledger index ("if a promise is not reachable from here, it has no home"); and no product surface may certify something it did not check, because a confident wrong result is the failure mode P-001 cannot tolerate.   [source: .project/product/0003-no-workarounds-for-bad-models.md + 0004-product-identity-parse-walk-emit.md (owner/HARD, [OWNER-VERBATIM, 2026-08-16]); .project/product/INDEX.md preamble (INHERITED); 0002-exact-owner-anchoring.md (agent/ratified); claude-pack/rules/capture-fidelity.md law 2 (owner/HARD)]
Falsifier: After Item 1 lands — the regenerated INDEX.md names no path to any promise entry, or an owner-verbatim quote's guarding assertion is dropped/weakened, or a P-00N Authority citation no longer resolves; or the contract seal still writes a bare `NaN` through the second encoder in the same file; or a live doc still advertises a gate that cannot fire.
Findings:
- spec-F1 [DO] The spec's own criterion is unreachable without editing the two `[OWNER-VERBATIM]` files it declares immutable, and it never says so. `product.sh` reads every index field from YAML frontmatter (`product.sh:29-35, 77-88`); none of the four entries has any — all begin `# P-00N — …`. So "`product.sh index` regenerates INDEX.md from the actual entries" requires adding `id/title/status/provenance/checked` frontmatter to P-003 and P-004, while `[HARD]` says their bodies are immutable and a material change is a supersession. The owner's harmonize ruling authorizes the direction but not the reach of the edit, so an implementer is left to improvise on owner-verbatim payload. — P-003/P-004 ([OWNER-VERBATIM], owner/HARD) + capture-fidelity law 2; mechanism at `product.sh:77-88` — disposition: spec must state the harmonization shape explicitly — rename + prepend a frontmatter block, body bytes below the block byte-identical to the pre-item state, verified mechanically (the epic Item 4 criterion "byte-identical" needs the same amendment to survive a prepended header). Not a BLOCK: the owner ruled "harmonize them to the new standard", which authorizes the change; only its bound is unwritten.
- spec-F2 [DO] The relocation requirement omits two classes of content the generated format cannot carry, and the omission is what the ledger calls the home condition. `regen_index` emits `- <id> · <title> · surfaces · checked` — no link, no filename, no provenance grade. The spec's `[INFERRED]` relocation list names the id rule, the ADR paragraph, the ADR-009 row, and the "Cited from" trail, but not (a) the four per-promise summary lines that carry each entry's grade in the index (`[OWNER-VERBATIM, 2026-08-16]`, `[AGENT] (ratified by owner…)`) and (b) index→entry reachability itself. The product-lens protocol resolves index-first and grades by provenance; a generated index with neither a path nor a grade makes the first hop guesswork. — .project/product/INDEX.md preamble, "if a promise is not reachable from here, it has no home" (INHERITED) + product-lens §1 SOURCES protocol (INHERITED) — disposition: add a criterion that the post-harmonization index resolves to entry files and exposes each entry's provenance grade — via a `provenance` frontmatter field surfaced in the generated line, or a documented `<id>-*.md` resolution rule stated in `.project/product/README.md`. Escalates with the smell below.
- spec-F3 [DON'T] The NaN fix is specified one line narrower than the defect, leaving the sealed on-disk bytes exposed. `[HARD]` pins only `contracts/serialize.py:28` (`canonical_json`, the fingerprint payload). `write_contract_json` at `serialize.py:34-36` — same file, same module docstring calling them "the same decision seen twice" — also omits `allow_nan=False`, and it writes the contract JSON that `PackageContract` hashes. With `ContractParameter.default_value: float | None` (`contracts/models.py:33`), a NaN default still produces a file containing bare `NaN`: invalid JSON, sealed with a confident digest. Fixing only the fingerprint form fixes the half that hashes and leaves the half that ships. — P-002, "a confident wrong number is the failure mode P-001 cannot tolerate" (agent/ratified) — disposition: extend the `[HARD]` requirement and the success criterion to both encoders in `serialize.py`. Falsifier (code): build a `ModelContract` whose `ContractParameter.default_value` is `float("nan")`, run the package seal, and assert the written contract file parses under `json.loads(..., parse_constant=raise)` — today it writes `NaN` and seals.
- spec-F4 [DO] The dead-gate correction stops at CLAUDE.md and leaves the same false claim in two live docs, one of them the register this item is triaging. `fallback_entry_points` is `set()` at both construction sites (`elaboration/project.py:287,322`; pinned by `tests/unit/test_warning_reconciliation_exact_route.py:167`), so V11 cannot fire. `docs/architecture/overview.md:63` still says generation "is also gated by a params-coverage check (V11) … and aborts", and `docs/architecture/modeling-assumptions.md:747-770` still lists V11 in "the pipeline enforces these rules" with its error text and a V11 note. A model author reading the ADR register is promised a refusal the toolchain will never issue — the inverse of the honest-refusal rule. — P-003 ([OWNER-VERBATIM], owner/HARD: ill-formed input is refused with a diagnostic, and the product does not claim behavior the standard/toolchain does not perform) — disposition: extend the criterion to every live doc asserting V11 fires (`overview.md:63,141`; `modeling-assumptions.md:747-770`), or state in Non-Goals why the register's Validation Rules table is deferred to Item 8 and record that a reader is knowingly left with a false gate until then. Reference documents 07/11/17/24 carry retiring banners and are out of scope.
- spec-F5 [DO] The citation criterion covers only inbound references, so a re-home can strand the owner-grade promise's own Authority. "Every citation of them still resolving" protects citations *pointing at* P-00N. P-001's Authority cites `docs/architecture/modeling-assumptions.md:588` (ADR-009) — and the spec's `[INFERRED]` names ADR-009 as the first candidate to re-home to `.project/adr/`, with the open question unresolved. Nothing binds a re-home to repointing P-001's citation or the INDEX back-registered row. Separately, the open question's live-citation enumeration is incomplete: `CLAUDE.md` ("`P-001` carries the design-search promise in the owner's own words"), `.project/CURRENT_WORK.md`, and `.project/active/dead-worktree-pins/product-lens.md` all cite `P-00N` and are not listed. — P-001 core ([OWNER-VERBATIM, 2026-08-13], owner/HARD) + inherited from epic_plan-F1 — disposition: restate the criterion in both directions ("every citation of a promise entry, and every path a promise entry cites, resolves after this item"), and re-derive the live-citation set mechanically rather than from the four-item list.
- spec-F6 [DO] The only mechanical guard on the owner-verbatim payload is treated as a path chore, and the rename makes two of its assertions unsatisfiable — which invites deleting them rather than re-expressing them. `tests/conformance/test_stop_parser_documentation_contract.py:208-245` asserts the P-003 quote text, the three P-004 step lines, and that both entry filenames appear in `INDEX.md`. The epic's deletion lock (epic_plan-F2) does not cover it — no ledger entry names it as Evidence — and after harmonization a generated index contains no filenames at all, so `assert "P-003-….md" in index` cannot pass under any rename. The spec says only "the test moves with them in the same change". — capture-fidelity law 2 over `[OWNER-VERBATIM]` payload (owner/HARD) — disposition: require that the quote-text assertions survive unweakened (only paths change) and that the index-reachability assertions are **re-expressed** against whatever the harmonized index guarantees (id + title, per spec-F2), never dropped; record the re-expression in the spec, not left to the implementer.
Smells fired: **7 — the proposed solution changes who owns an invariant without saying so.** The ledger's contract "if a promise is not reachable from here, it has no home" is today owned by hand-written index prose; handing INDEX.md to `product.sh` transfers that invariant to a generator whose output format cannot express reachability, and the spec does not name the transfer. Must escalate into the spec stage's judgment and be disposed with spec-F2 before design starts.
Gate: DISPOSED (spec-F1, spec-F2, spec-F3, spec-F4, spec-F5, spec-F6)
```

### Dispositions applied to the spec

| Finding | Where it landed |
|---|---|
| F1 | New `[HARD]`: harmonization is rename-plus-prepend, bytes below the block byte-identical, verified mechanically. Epic Item 4's "byte-identical" criterion amended to match. |
| F2 | New `[HARD]` and success criterion: the regenerated index resolves to entry files and exposes provenance grade. Relocation list extended with the per-promise grade lines and reachability itself. |
| F3 | Widened to **both** encoders in `serialize.py` and carried out of this item into `[SERIALIZE-NAN-SEAL]`, with the NaN falsifier test as its acceptance. `[OWNER, 2026-08-20]` |
| F4 | Widened to `overview.md:63,141` and `modeling-assumptions.md:750-785` and carried out of this item into `[V11-DEAD-GATE-DOCS]`. The doc claims and the dead code now have separate homes: docs in the standalone item, code retirement in REPO-CLEANUP Item 8. `[OWNER, 2026-08-20]` |
| F5 | Citation criterion restated in both directions; Open Question now requires the live set to be re-derived mechanically, and records the 13 sites found on 2026-08-20. New `[INFERRED]`: re-homing ADR-009 repoints `P-001`'s Authority in the same change. |
| F6 | New `[HARD]`: quote assertions survive unweakened, index-reachability assertions re-expressed against id+title, never dropped. |

**Smell 7 disposition:** the invariant transfer is now named in the spec's Problem section — the
ledger's "reachable from here" contract moves from hand-maintained prose to a generator whose
format cannot currently express it, and this item owns leaving reachability and grade demonstrable
afterwards.

---

## Run 2 — audit stage, 2026-08-21

Gate: **DISPOSED** (audit-F1 … audit-F5). Smells 1 and 6 fired; both are resolved in
`audit.md` "Product Judgment". Run 1's findings were all disposed at spec time and remain disposed;
the epic's live gate (`.project/backlog/epic_repo_cleanup.md` Product-Lens) is DISPOSED with no
BLOCK. Nothing in either ledger forbids certification.

The auditor verified each finding before disposition:

- `audit-F1` confirmed and narrowed — `diff` against the pack README shows the section heading at
  `:36` and the clause "it lives in `.project/adr/`" at `:40-43` edited in place, plus an appended
  repo-local section. The in-place edit was forced: the pack sentence asserts a single decision
  home, which I6 forbids. The installer does not protect the file, but
  `test_no_document_claims_a_single_adr_home` asserts `two decision registers` in it, so a clobber
  fails the suite rather than passing silently.
- `audit-F2` confirmed — the two strings `only adr home` / `single adr home` never existed in the
  tree. The positive arm (both register paths plus "two decision registers" present) is the guard.
- `audit-F3` confirmed as stated; mitigated by ordering — the epic's Item 3 scope step 2a is the
  carrier, and Item 3 precedes the Item 5 purge.
- `audit-F4` confirmed — `.project/adr/0001` has `promoted_to: null` while `CLAUDE.md` and
  `.project/product/README.md` restate its rule. `adr.sh` has no `promote` subcommand.
- `audit-F5` already owner-ratified (`[AGENT] (ratified by owner, 2026-08-21)`, spec `[HARD]`).
  Auditor's count is five repointed lines (0002:1, 0003:1, 0004:3), matching the spec; the lens's
  "four" is a miscount.

```
## audit — 2026-08-21 — rev 3566fdd (.project/active/scaffolding-register-boundary/)
Point (re-derived): The two registers exist so a cold agent months later gets truth without re-derivation — routing settled once by audience, ids/status/index script-owned, entry bodies append-only, and every durable claim reachable from a durable surface.   [source: .project/adr/0001-route-decisions-by-who-they-bind.md (owner); .project/backlog/epic_repo_cleanup.md:63-93 [OWNER, 2026-08-20] (owner); agentic-project-init/project-pack/{adr,product}/README.md (INHERITED)]
Falsifier: A durable statement about the registers that a cold agent would read as true but that no mechanism keeps true — a hand-forked pack file, a filed body silently rewritten, an index id resolving to zero or two entries, or a triage outcome whose only record sits in a directory the pack README declares non-durable.
Findings:
- audit-F1 [DON'T] `.project/product/README.md` is a hand-fork of the upstream pack README — local text rewritten into the pack's own "Register boundary" section — while `adr/README.md`, `adr.sh`, and `product.sh` are byte-identical to the pack; the next pack refresh must hand-merge or clobber it, and nothing detects the divergence. — project-pack/product/README.md (INHERITED) + .project/adr/0002's own Why, which rejected a local fork (agent/ratified) — Smell 1 — falsifier: `diff project-pack/product/README.md .project/product/README.md` returns 25 lines while the other three installed pack files return none — disposition: DISPOSE (record the local delta as an explicit repo-local appendix below the pack text, or file it as a pack change upstream)
- audit-F2 [DON'T] `test_no_document_claims_a_single_adr_home` enforces its negative arm with three literal lowercase strings; only one ever existed in this repo, and "only adr home" / "single adr home" have never appeared anywhere in the tree — the negative arm passes by matching one deleted phrasing, not by checking the invariant. — item Success Criterion "no remaining claim of a single home", from epic_repo_cleanup.md:88-90 (owner) — Smell 6 — falsifier: add "ADRs live only in modeling-assumptions.md; `.project/adr/` is not a decision home" to CLAUDE.md — all 14 safe-contract tests still pass — disposition: DISPOSE (assert the positive convention only, or drop the two dead strings and say plainly that the negative arm pins one historical phrasing)
- audit-F3 [DO] The triage outcome for ADR-007 and ADR-009 — recorded as misfiled, builder-facing — has no durable home: modeling-assumptions.md §7 and §9 carry no marker, and the sole record is .project/active/scaffolding-register-boundary/adr-triage.md, a path the pack ADR README calls working state and that epic Item 5 will clear. — epic_repo_cleanup.md:190-194 "record the outcomes — move nothing" [OWNER, 2026-08-21] (owner obligation; durability gap is AGENT inference) — falsifier: archive .project/active/ and read §7 cold — nothing says it is recorded as belonging in the other register — disposition: DISPOSE (Item 3 carries the re-home; until then the outcome needs a durable pointer)
- audit-F4 [DO] .project/adr/0001 — the [OWNER] entry whose routing rule is restated in full in both CLAUDE.md and .project/product/README.md — carries `promoted_to: null`, while 0002 and 0003 declare theirs. 0001's own invariant reads "File one ruling in one register. Other documents cite it rather than duplicate it." — .project/adr/0001 (owner) + pack ADR README frontmatter table (INHERITED) — Smell 1 (second instance) — falsifier: `grep promoted_to .project/adr/*.md` — disposition: DISPOSE, not BLOCK: the owner required the CLAUDE.md paragraph be corrected (epic:88-90), so the duplication is sanctioned; only the bookkeeping is missing
- audit-F5 [DON'T] The P-00N → 000N migration edited three already-filed entry bodies (link lines in 0002/0003/0004), against "a body is immutable after filing." — project-pack/product/README.md Lifecycle (INHERITED) — falsifier: body-byte diff vs da15f14 is non-empty for three of four entries — disposition: DISPOSE. Verified minimal and forced: the diffs are only intra-ledger link retargeting made necessary by the rename; 0001 is byte-identical and no promise text, quote, grade, or bound changed.
Verified clean: owner-verbatim payload in all four entries survives byte-identical; product.sh index and adr.sh index regenerate the committed INDEX.md byte-for-byte; every indexed id resolves to exactly one sibling entry; both engines are byte-identical to the pack. The 3 failing tests in the contract file are the pre-existing missing-artifact-manifest limitation.
Smells fired: 1 (F1, F4), 6 (F2) — escalated into the audit's leading judgment.
Gate: DISPOSED (audit-F1, audit-F2, audit-F3, audit-F4, audit-F5)
```
