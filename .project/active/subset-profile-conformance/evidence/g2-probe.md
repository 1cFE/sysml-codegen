# G2 probe: a usage override of a definition-owned referenced bound (P1.1, PD10)

**Result: the pinned generator ignores the override, and generation succeeds.** `tuned : Site { attribute :>> n default 3; }` gets 2 `racks` occurrences, the same as the control `small : Site`, whose definition bound is `n default 2`. No code is reported. So G2 is a silent loss today, and P4's G2 case asserts the occurrence count at the `occurrences` seam (2, not 3), not a refusal.

## What was run

- Revisions: sysml-codegen `d256845d` (`src/` identical to `b5663c07`), agentic-mbse `882edc6a` (sibling worktree, editable install), SysIDE 0.8.4, licensed. Run before any 2a code change.
- Model: `spikes/g2/model.sysml`, the minimal form of Item 1 spike F1's `f1_referenced_bounds` (F1 Surprise 2(b)), with a calculation so the model has something to generate:

  ```sysml
  package g2 {
      private import ScalarValues::*;
      calc def Twice { in v : Real; return r : Real = 2.0 * v; }
      part def Rack { attribute p : Real = 1.0; calc t : Twice { in v = p; } }
      part def Site { attribute n : Integer default 2; part racks : Rack[n]; }
      part small : Site;
      part tuned : Site { attribute :>> n default 3; }
  }
  ```

- Command, from the codegen root after sourcing the license: `uv run python .project/active/subset-profile-conformance/spikes/g2/probe.py`. The script runs spike S1's generator half (`spikes/s1/harness.py`: `run_codegen` with the three screen entry points tripwired) and counts `racks` occurrences per parent from the instance graph spied on `elaborated_pipeline.elaborate_model_paths`.

## Output

```
generated=True codes=[] stubs=[]
small: racks occurrences=2 indices=[0, 1]
tuned: racks occurrences=2 indices=[0, 1]
```

The screen tripwire was not hit.

## Why (from the code, not re-derived here)

Item 1 spike F1 located the cause: `_modeled_integer_bound` (`elaboration/occurrence.py:726-763` at `b5663c07`) looks only at definition-owned writers when the multiplicity's owner is a part def, so the usage-level redefinition of `n` is never read.

## Not checked

- Whether SysML v2 / KerML semantics require 3. That is the `kerml-expert` question P4 asks for G1 and G2 together (PD10).
- Other override spellings (`attribute :>> n = 3;`, a redefinition through a specialized part def). F1's `BigSite :> Site { attribute :>> n default 4; }` gets 4, so a definition-level override is read; only the usage-level one is ignored.
