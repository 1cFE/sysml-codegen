# Design Review: Trusted Package Bootstrap and Seal Provenance (Lifecycle Item 7)

**Design:** `.project/active/constraint-lifecycle-package-trust/design.md`
**Spec:** `.project/active/constraint-lifecycle-package-trust/spec.md`
**Review File:** `.project/active/constraint-lifecycle-package-trust/design-review.md`
**Date:** 2026-07-20
**Reviewer posture:** independent; verified against live code in both repos
(sysml-codegen HEAD `abe6c4d`; TEAx HEAD `db23719`, i.e. `d545701f` + `db23719`).

---

## Fundamental Assessment

**Sound.** The two-anchor shape is the right answer to this spec, and it is built by
extending machinery that already exists rather than inventing new abstractions:

- **Consumer side (attack a).** Hashing the package-local `verify.py` bytes against a
  runtime-vendored constant *before* `exec_module` is the correct fix, and it genuinely
  kills the unconditional-success verifier before any package code runs (verified below).
  Choosing a **hash, not a second verifier** (D1) is the correct call — a second TEAx-side
  verifier would be exactly the drift the epic forbids, and the hash duplicates no
  semantics. B3 (no sysml-codegen import) is preserved: a 64-char constant is the identical
  move to the version literal TEAx already vendors at `package_load.py:22`.
- **Producer side (attack b).** A generation manifest consulted at re-seal, gated at the
  **CLI layer** (D4) so the certified seal/verify walkers stay untouched, is the right
  structural choice.
- **D3 (the flagged risk).** The stale-fixture drift is real and the re-seal direction is
  correct (verified below). Accepting a set of historical hashes would institutionalize the
  very multi-image-per-version drift the spec exists to kill.

The design is not over-engineered. It adds one constant, one covered artifact, and one
CLI-level gate. No new walker, no merged boundary, no second schema authority.

**So the verdict is Approve-with-revisions, not Rework.** The revisions below are about
*honesty and coherence of the claims*, not about the mechanism. Two of them matter for
Item 13's composed proof, where someone will cite "laundering closed" and "no untrusted
code runs" as settled — and one of those is closed only against a weaker adversary than the
prose implies, and the other has a TOCTOU seam.

---

## Priority Findings (as tasked)

### P1 — D3 stale-fixture drift: CONFIRMED, and re-seal is the right direction

Verified on disk (TEAx HEAD):

| fixture | `contracts/verify.py` sha256 | seal `runtime_contract_version` |
|---|---|---|
| `sealed_package/package_live` | `86de6dd3…ab7071d` | `1.0.0` |
| `f1_arithmetic/package_live` | `24eb3565…a400276` | `1.0.0` |
| canonical `src/sysml_codegen/contracts/verify.py` | `ad0a855a…c67284` | (current 1.0.0) |

Both fixtures carry pre-current verifier bytes labeled `1.0.0`. verify.py's bytes changed
across at least three images (`24eb356` → `86de6dd` → `ad0a855`) with the version literal
pinned the whole time — the exact silent drift the spec targets. Under D1 authentication the
two fixtures would be rejected. The design surfaces this instead of resolving it silently,
which is correct per the surfacing law.

`24eb3565…` is also the value pinned as `REVIEWED_VERIFY_SHA256` in
`tests/conformance/test_fingerprint_stability.py:32` — i.e. a *prior* verifier policy the
stability test deliberately keeps around. So the drift is not accidental garbage; it is
older policy bytes that were re-sealed without a version bump. **D3's resolution (re-seal
the fixtures to canonical + one-image-per-version going forward) is the right call.**

One clarity item for the design (Minor, below): the remediation re-seals the fixtures to
`ad0a855` while keeping `runtime_contract_version = "1.0.0"`, i.e. it does *not* bump. This
is consistent — `ad0a855` is already the declared 1.0.0 canonical, and the old fixture bytes
were never a legitimate separate version — but D3's own wording ("any byte change requires a
bump") reads as if it should bump. State plainly that `ad0a855` *is* the (now-single) 1.0.0
image and the fixtures are being corrected to it, so no reader mistakes this for a violation
of bump-on-change.

### P2 — Hash-anchor kills attack (a) before exec, but there is a TOCTOU seam

The mechanism is sound. Today `_load_verify_package` (`package_load.py:38-51`) runs
`spec.loader.exec_module(module)` at `:50` with **no authentication first**, then trusts the
result (`:74-84`). Inserting a `read_bytes → sha256 → compare to TRUSTED_VERIFIER_SHA256`
check before `:50`, raising on mismatch, genuinely rejects an `ok=True` stub before any
package code executes. `spec_from_file_location` / `module_from_spec` do not run the module
body; only `exec_module` does. So INV-A holds *as long as the bytes that are hashed are the
bytes that execute.*

**They are not, as written.** The design's data flow hashes the file, then calls
`exec_module`, which **re-reads the file** via the source loader. That is two reads of an
attacker-controlled path with a window between them. An adversary who can win a local
filesystem race (a concurrent writer during load — the same adversary who planted the
malicious `verify.py` in the first place) presents good bytes to the hash check and
malicious bytes to `exec_module`. The spec's criterion is literally "must not execute
package-local code … ahead of authenticating it"; TOCTOU means unauthenticated bytes can
execute. See **Major 1** for the cheap fix.

**Trusted-hash channel.** The vendored `TRUSTED_VERIFIER_SHA256` lives in TEAx source
(`package_load.py`, module constant, exactly like `:22`). It is runtime-owned; a package
cannot influence it. This channel is genuinely unforgeable by the package. Legitimate update
is manual re-vendoring, and the design is honest that the cross-repo sync is a mitigated,
not eliminated, process risk. One caveat: the design says a "TEAx skew test" enforces INV-B,
but TEAx cannot import codegen (B3), so that test can only check the vendored hash against
its *own re-sealed fixtures* — internal consistency, not agreement with the current codegen
canonical. INV-B's cross-repo half is enforced only by the codegen-side drift test plus
manual discipline. State that split so INV-B isn't read as a closed loop (Minor).

### P3 — Version policy fails closed, but the accepted-versions shape is coupled to the single hash

Fail-closed both directions is satisfied: the loader reads `seal.runtime_contract_version`,
checks it against its own policy, and rejects with a named diagnostic in either skew
direction; the bare `"1.0.0"` literal at `:22` is deleted (no survivor); passing the seal's
own version into `verify_package` makes its symmetric `==` a satisfied no-op so acceptance
lives only in the loader (D2). Good.

**Rollback scenario — no security hole, correctly fail-closed.** Older legit package
(sealed `1.0.0`, bytes `ad0a855`) meets newer runtime (accepts only `2.0.0`, vendors the
`2.0.0` hash): the package is rejected on *both* the version policy *and* the hash anchor.
Safe, named, fail-closed. The only cost is that old packages need re-sealing to run on a new
runtime — which is exactly the fixture re-seal the design already does. Intended.

**But the accepted-versions shape is not the free open question the design says it is.**
The design vendors a **single** `TRUSTED_VERIFIER_SHA256` and leaves "single-version set vs
range" open in the handoff. Those are coupled: TEAx can only authenticate a package whose
`verify.py` matches the one vendored hash, and D3 ties one verify.py image to one version.
So a *range* or multi-version accepted set is meaningless with a single hash — accepting
version V requires vendoring V's canonical hash, which a single constant cannot do. INV-B is
already written singular ("*the* accepted runtime_contract_version"). See **Major 3**: close
the open question to single-version, or specify a version→hash map (and drop the "nothing to
drift" simplicity claim if you do).

### P4 — Manifest / laundering: naive attack (b) is closed; the producer-side anchor is not "forgery-proof"

The gate closes the spec's attack (b) as written. Verified: `seal_package`
(`seal.py:93-122`) hashes whatever is on disk minus the seal and `__pycache__`, and
`cmd_seal` (`cli/__init__.py:728-768`) gates only on no-symlinks + prior-model-contract. A
foreign `modules/evil.py` dropped and re-sealed today is hashed into `artifact_hashes`
(`:762`) as covered. Under D5, `evil.py` is not in the enumerated codegen set and not under
`handwritten/**` or a runtime glob → hard-fail. **Enumerated-not-glob for the codegen class
is the right choice** — it stops glob-class abuse (you cannot place a file into "codegen" by
directory; you must be in the explicit list). A foreign file under `handwritten/**` is
admitted as *handwritten*, which the spec explicitly permits ("recorded as non-codegen").

**The overclaim is the trust root, and it breaks the design's own symmetry.** The Core
Concept says the fix "plants forgery-proof anchors on each side" and that a foreign file
"cannot be laundered." That is true on the **consumer** side (the TEAx hash constant is
genuinely unforgeable by the package). It is **not** true on the **producer** side. The
manifest's authenticity anchor is the *prior `package_contract.json` on disk* — and at
re-seal, that file is as attacker-writable as the foreign file itself. The realistic
attack-(b) adversary is whoever has write access to the source tree between generation and
re-seal (a malicious PR, a compromised dep, a supply-chain inject). That same adversary can
rewrite the manifest to list `evil.py` as codegen-produced *and* rewrite the prior seal's
`artifact_hashes` to record the tampered manifest's hash — a self-consistent forgery the
gate cannot detect, because nothing cryptographically binds the prior seal to a trusted key.

So the gate's real strength is: it defeats a **non-collusive** injection (an attacker who
adds a file but does not also rewrite manifest + prior seal — e.g. malware that does not know
the scheme, or a partial tamper). It is defense-in-depth, not an authenticity boundary. That
is a legitimate and useful contribution — but the prose promises more than a same-privilege
adversary allows. This matters for Item 13: "laundering closed" will be cited as settled.
See **Major 2** — state the boundary and add a Non-Goal (seal signing) so the composed proof
inherits the honest scope. Note this cannot be fixed with a better mechanism inside Item 7:
the re-seal runs on the producer side, which has no runtime-owned secret to anchor to.

**Manifest completeness is an unstated, load-bearing obligation.** A real generated package
(verified from the `f1_arithmetic` fixture) covers ~22 files across seven regions —
`IMPLEMENTATION_BACKLOG.md`, `primitives.py`, `__init__.py`, `inputs/*`, `modules/*`,
`pipelines/*`, `schemas/*`, `tests/*`, plus `handwritten/__init__.py`. The enumerated
codegen set must list **every** generated file, or INV-E hard-fails a *legitimate* re-seal
(any covered file not in the set and not under a glob is unaccounted). The design grounds
this on B3 / `_generate_stencils` "tracking per-file provenance" — but that function only
tracks **counts** (`stats = {"new", "preserved", "regenerated"}`, `cli/__init__.py:421+`),
and it is one emitter among many (modules, schemas, inputs, `__init__`, pipeline, contracts,
backlog). Building the enumerated set by per-emitter path collection is fragile: miss one
emitter and legit re-seal false-fails. The robust construction is "codegen_produced = all
covered files at first seal, minus `handwritten/**`, minus runtime globs," captured when the
tree is known-clean. That also makes B3 largely a red herring — the `handwritten/**` glob
already partitions human-owned from codegen-owned; per-file provenance is not needed. See
**Major 4**.

Residual (in-scope, note only): `handwritten/**` is an admit-and-execute region — stencils
there are imported and run. A foreign file dropped under `handwritten/` is admitted (as
handwritten) and will execute if imported. This is the existing human-owned trust model, not
a regression, and the spec explicitly allows admitting foreign files under a non-codegen
class. Worth one honest sentence in the design so the boundary is on record.

### P5 — Certified scope stays green: CONFIRMED

I read the actual assertions in all four named tests. They survive an additive
`generation_manifest.json` because none pins an exact covered-set or absolute
fingerprint/hash value:

- `test_fingerprint_stability.py` — every assertion is **relative/self-consistent**: two
  generations equal each other, and `executable_fingerprint == sha256(sorted artifact_hashes)`
  recomputed inline. Adding the manifest to both sides preserves both. The manifest content
  is verify.py-byte-independent (it lists `contracts/verify.py` as a *path*, not a hash), so
  `test_policy_update_changes_only_verifier_hash_and_derived_fingerprint` still finds the
  two sides equal after popping `verify.py`. Stays green **unchanged**.
- `test_seal_step9.py` — uses `in` / `not in` on `artifact_hashes` (`:101-103`), a per-file
  verify.py hash check (`:58`), and a diagnostics-list equality on a *violation* case
  (`:84`). No exact-set, no `len()`. The re-seal test (`:109-124`) edits a handwritten
  stencil and expects `cmd_seal == 0` — it now exercises the new gate and *should* stay
  green because a `handwritten/**` edit is admissible. Stays green unchanged (and validly
  covers the new gate's happy path).
- `test_contract_models.py:175-177` — relative equality between two seals. Additive.
- `test_verify_package.py` — mutation/tamper tests on seals the test builds itself;
  `verify_package` does not require a manifest to exist (the gate is in `cmd_seal`, not
  `verify_package`). Unaffected.

**Correction to the design's own churn claim (Minor):** Potential Risks says
"fingerprint-stability fixtures must be regenerated." They must **not** —
`test_fingerprint_stability.py` pins no absolute fingerprint. Only `baseline_outputs`
(byte-identity fixtures, *not* in the named stay-green list) churn. The design *overstates*
the churn, which is harmless but muddies the otherwise-correct "stay green unchanged" claim.
Tighten it.

The gate is added *after* `ensure_package_tree_is_link_free` in `cmd_seal` and reuses its
returned entries (currently discarded at `:748`), touching neither walker. INV-D / INV-G
hold. Nothing reopens the certified scope.

### P6 — Phasing: codegen-first is genuinely backward-compatible

Verified. New codegen package = old package + `generation_manifest.json` (another covered
file) with `verify.py` bytes unchanged (`ad0a855`). Old TEAx loads it: `_load_verify_package`
execs the unchanged verifier, `verify_package` hashes the manifest consistently (it is on
disk and in `artifact_hashes`), version `"1.0.0"` matches the old literal. Loads fine.
Forward direction holds. The reverse (new TEAx loading old, pre-`ad0a855` packages) is
correctly fail-closed — which is why the fixture re-seal is required and why I checked scope:
**only those two fixtures exist** (a repo-wide search for sealed `verify.py` fixtures found no
others), so the re-seal change set is complete.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns
Every success criterion has a design element, and provenance is carried faithfully
(`[INHERITED]` intents → D1/D2/D5; `[HARD]` walker boundary honored; `[NEED]` simplicity met
by deletion of the bare literal and the symmetric-`==` authority). The concern is that the
design's *prose* claims more than the mechanism delivers against a same-privilege re-seal
adversary (P4 / Major 2). The spec's attack (b) is written naively (drop a file, re-seal) and
is satisfied; the design's "cannot be laundered" framing outruns that. Also the version-story
open question is under-constrained (P3 / Major 3).

### 2. Pattern Consistency
**Assessment:** Pass
Extends existing precedent throughout: the vendored version literal (`:22`), the pinned
verifier hash (`REVIEWED_VERIFY_SHA256`), the INV-8 drift guard, the CLI-level seal step.
No new patterns invented. `versions.py` remains the single publish point.

### 3. Abstraction Quality
**Assessment:** Pass
A constant, a covered JSON artifact, and a CLI gate — the right weight for the problem.
Keeping the gate out of the pure `seal_package` (D4) is a clean separation and the reason the
certified walker stays untouched.

### 4. Duplication Avoidance
**Assessment:** Pass
The hash-not-second-verifier decision (D1) is the whole point: no duplicated verification
semantics. The deliberate seal/verify walker duplication is correctly preserved, not
collapsed. The design *reduces* duplication by deleting the bare version literal's authority.

### 5. Data Structure Clarity
**Assessment:** Concerns
The manifest schema is explicit and typed by example. Two gaps: (a) the completeness
obligation on `codegen_produced` is unstated (P4 / Major 4) — the reader cannot tell that
*every* generated file must appear or that the safe construction is tree-minus-globs; (b)
whether `runtime_contract_version` lives in the manifest or is read only from the seal is
left open, and the manifest currently carries it redundantly with the seal — pick one home.

### 6. Route Safety
**Assessment:** Concerns
Load-path and re-seal-path routes are explicit and fail-closed. The TOCTOU seam (P2 / Major
1) is the one route-safety gap: the authenticated bytes and executed bytes can differ.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns
Decisions each name their rejected alternative — good. The bets are where the honesty gap
sits:
- **B3 is overstated.** "Codegen knows the exact provenance class of every file" is grounded
  on `_generate_stencils`, which tracks counts, not paths, and is one emitter of many. The
  info is *derivable* at generation (tree-minus-globs), but not *retained* per-file as B3
  implies. If false in the fragile reading, re-seal false-fails legit packages (Major 4).
- **Hidden bet — producer-side anchor is unforgeable.** The Core Concept asserts
  forgery-proof anchors "on each side." The producer-side anchor (prior seal on disk) is
  forgeable by the same adversary who mounts attack (b). This unstated, wrong-in-the-strong-
  reading bet is the most expensive one here because Item 13 will inherit it (Major 2).
- **Hidden bet — manifest content is verifier-byte-independent.** Load-bearing for
  `test_policy_update` staying green and for a stable manifest hash across verifier edits.
  True in the illustrative schema (paths, no hashes), but never stated. Make it explicit.

### 8. Reader Comprehension
**Assessment:** Pass
The mental model (anchors the package cannot forge, one per side) is stated plainly before
mechanism, and the data-flow blocks are clear. The one comprehension risk is that the "each
side" symmetry actively misleads — the two anchors are not equally strong, and a careful
reader will trust the producer side more than it deserves. Fixing Major 2 fixes this too.

---

## Issues by Severity

### Critical
None. The mechanism is sound; nothing here warrants rework.

### Major
- **Major 1 (TOCTOU).** Authenticate the exact bytes that execute. Read `verify.py` once,
  hash, and on match `exec(compile(bytes, str(verify_path), "exec"), module.__dict__)` —
  do not fall through to `spec.loader.exec_module`, which re-reads the file. As written, the
  hashed bytes and executed bytes are two separate reads of an attacker-controlled path.
- **Major 2 (producer-anchor honesty).** The re-seal provenance gate defeats non-collusive
  file injection, not a same-privilege adversary who also rewrites the manifest and prior
  seal (both on-disk, unsigned). Restate the Core Concept's "forgery-proof on each side" to
  distinguish the strong consumer anchor from the defense-in-depth producer gate, and add a
  Non-Goal: "seal authenticity via signing / a trusted key is out of scope; the gate closes
  the drop-a-file laundering attack, not a coordinated re-seal." Protects Item 13's proof.
- **Major 3 (version/hash coupling).** Close the accepted-versions open question to
  single-version, or specify a version→hash map. A single vendored `TRUSTED_VERIFIER_SHA256`
  forecloses a multi-version accepted set; a "range" is incoherent with one hash. Align INV-B
  (already singular) and the handoff.
- **Major 4 (manifest completeness).** State that `codegen_produced` must enumerate every
  generated covered file (or a legit re-seal hard-fails), and specify the construction —
  recommend "all covered files at first seal minus `handwritten/**` minus runtime globs,"
  which guarantees completeness and makes B3's per-file claim unnecessary.

### Minor
- D3 wording: make clear `ad0a855` *is* the (now-single) 1.0.0 image; re-sealing fixtures to
  it is a correction, not a bump-on-change violation.
- INV-B cross-repo half is enforced by the codegen drift test + manual discipline, not by the
  TEAx skew test (which can only check internal consistency under B3). Say so.
- Correct the Potential-Risks churn claim: `test_fingerprint_stability` stays green
  unchanged; only `baseline_outputs` churn. Remove "fingerprint-stability fixtures must be
  regenerated."
- Note the residual `handwritten/**` admit-and-execute surface (in scope, acceptable) so the
  trust boundary is on record.
- Pick one home for `runtime_contract_version` (manifest vs seal); avoid the redundant copy.

---

## Recommendations

1. **Major 2 and Major 4 first** — they are about what Item 7 actually guarantees, and Item
   13 composes on those words. Both are cheap: a paragraph + a Non-Goal for Major 2; a
   sentence + the tree-minus-globs construction for Major 4.
2. **Major 1** — one-line change to how the verifier is executed; closes the TOCTOU the
   spec's own criterion names.
3. **Major 3** — decide single-version now; it is the natural reading and avoids the plan
   picking an incoherent range.
4. Sweep the Minors (D3 wording, INV-B enforcement split, churn correction, handwritten
   surface note, version-field home). None blocks the plan.

The five decisions (D1–D5), the invariants, the sysml-codegen-first phasing, the stable
`verify.py` bytes, and the untouched walker boundary are all sound and should carry into the
plan unchanged.

---

## Resolutions

Round 1 applied to `design.md` (2026-07-20):

- **Major 1 (TOCTOU) — applied.** Load data-flow and TEAx architecture bullet now state: read
  verifier bytes once, hash, and on match `exec(compile(bytes, str(verify_path), "exec"), ...)`
  — never `exec_module` (which re-reads). INV-A reads against the executed bytes.
- **Major 2 (producer-anchor honesty) — applied.** Core Concept rewritten to distinguish the
  unforgeable consumer anchor from the defense-in-depth producer gate ("defeats non-collusive
  injection, not a same-privilege adversary"); the hidden "forgery-proof on each side" bet
  removed. New Non-Goal: seal authenticity via signing / trusted key out of scope; Item 13
  inherits the honest scope.
- **Major 3 (version/hash coupling) — applied.** Accepted-versions policy closed to
  single-version; the single-vs-range open question removed from the handoff; TEAx bullet and
  INV-B state one vendored hash = one image = one version.
- **Major 4 (manifest completeness) — applied.** D5, B3, Component Overview, and manifest
  schema now specify `codegen_produced` = tree-minus-`handwritten/**`-minus-runtime-globs at
  first seal, with the completeness obligation stated; B3 reworded off the fragile per-file
  claim.
- **Minors — applied.** D3 wording ("`ad0a855` *is* the single 1.0.0 image; correction, not a
  bump"); INV-B enforcement split (codegen drift test + manual discipline; TEAx test = internal
  consistency only); churn corrected (`test_fingerprint_stability` stays green unchanged, only
  `baseline_outputs` churn); `handwritten/**` admit-and-execute residual recorded as a Non-Goal;
  `runtime_contract_version` home fixed to the seal only (dropped from the manifest). New bet
  B3a (manifest content is verifier-byte-independent) added.

---

**Overall:** Approve-with-revisions
**Next Steps:** Record resolutions above, then return to the design-agent session (or re-run
`/_my_design`) pointed at this review to incorporate the four Major revisions and the Minors.
The reviewer does not edit the design. Max two rounds; this is round 1.
