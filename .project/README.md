# Project Management

This folder contains project planning, tracking, and documentation.

---

## Workflow Overview

### 1. Accumulating Backlog

**Collecting Needs**:
- **Research & Analysis**: Running research reports, web searches, collecting data to understand what needs to be done
- **During Development**: Issues identified while running/writing code
- **External PM**: Requirements from external project management systems

**Creating Epics**:
- Capture outcomes and goals
- Note known pieces of work (details come later during decomposition)

---

### 2. Prioritization

1. **User prioritizes** using their own methods
2. **Update BACKLOG.md** via `/_my_status` command - reorganize, set priorities
3. **Epic decomposition** (before or after prioritization, e.g., to estimate effort):
   - Organize into **parts** if needed (logical groupings)
   - Break down into **items** with numbering (e.g., `4.2` = Part 4, Item 2)

---

### 3. Epic Execution

Iterate through items in the epic. Each item runs the standard pipeline of `/_my_*` stages.

**For the canonical, current flow and when/how to use each stage, run `/_my_pipeline`** (installed
with claude-pack). This README does not carry its own copy of the sequence — `/_my_pipeline` is the
single source, so it can't go stale here.

**As the epic progresses**: Add or insert new items as you learn more. Follow the same process for each.

---

### 4. Item and Epic Close — the standing rule `[OWNER, 2026-08-23]`

**Close = record, then delete. Git history is the archive.** There is no `completed/` folder.

1. **Record what is durable**: settled decisions go to the register `.project/adr/0001` routes
   them to; implemented promises to `.project/product/`; investigation results worth keeping to
   `research/`. An item whose knowledge is captured has nothing left to archive.
2. **Delete the item folder** from `active/` in the closing commit. The commit message names the
   item; `git log` finds it forever. Never leave a closed item in `active/`, and never copy it
   anywhere first.
3. **Update docs**: `CURRENT_WORK.md` and `BACKLOG.md`.

This replaces the old archive-to-`completed/` flow, whose result was 551k lines of duplicate
process history (REPO-CLEANUP, 2026-08-23).

---

## Key Files

| File | Purpose |
|------|---------|
| `CURRENT_WORK.md` | What's active RIGHT NOW - single source of truth |
| `product/INDEX.md` | Generated index of implemented product promises — what the product is for (convention: `product/README.md`) |
| `adr/INDEX.md` | Generated index of load-bearing decisions (convention: `adr/README.md`) |
| `backlog/BACKLOG.md` | Prioritized list of epics |
| `backlog/epic_*.md` | Individual epic definitions |

---

## Folder Structure

```
.project/
├── CURRENT_WORK.md           # Active work tracking
├── backlog/
│   ├── BACKLOG.md            # Prioritized epic list
│   └── epic_*.md             # Epic definitions
├── active/
│   └── {item_name}/          # Work-in-progress items
│       ├── spec.md
│       ├── design.md
│       └── plan.md
├── adr/                      # Decision records (append-only, script-managed)
├── product/                  # Product promise ledger (append-only, script-managed)
├── scripts/                  # Utility scripts (adr.sh, product.sh, get-metadata.sh)
└── research/                 # Deep investigations (git history is the archive of closed items)
```

---

## Item Numbering

Items within an epic use hierarchical numbering:
- `1`, `2`, `3` - Simple sequential items
- `4.1`, `4.2`, `4.3` - Items within Part 4
- Parts group related items logically

---

## Commands

This README does not carry a command catalog — a copy here would drift. Two live sources:

- **`/_my_pipeline`** — the canonical stage map and when to use each stage.
- **The toolkit README's Command Reference** (in the agentic-project-init repo) — one line per command, including shortcuts, modes, and project-management helpers.

---

**Last Updated**: Template
