# Task: summarize completed work-item folders into structured records

You are reconstructing the execution history of a repository's `.project/completed/` archive.
Someone will later read all these records joined into one chronological document to decide which
past decisions still matter. Your records are the only thing they will read — the folders
themselves will not be re-read.

## Input

Your batch file lists folder names, one per line. Each is a directory under
`/home/reid/1cfe/sysml-codegen/.project/completed/`.

## For each folder

Read its markdown only (`*.md`). Ignore `.json`, `.log`, `.py`, `.txt` — they are machine output.
In large folders read `spec.md`, `design.md`, `audit.md`, and any close/report/verdict file first;
`plan.md` files are step-by-step narration and are the lowest value — skim or skip.

Write exactly one JSON file per folder to:
`/tmp/claude-1000/-home-reid-1cfe-sysml-codegen/9d46a5da-484d-41a3-b1e7-5a025da8f27a/scratchpad/spine/<foldername>.json`

## Schema — all fields required

```json
{
  "dir": "20260813_constraint-coverage-policy",
  "date_start": "2026-08-12",
  "date_end": "2026-08-13",
  "epic": "CONSTRAINT-SEMANTICS",
  "item_number": "Item 3",
  "title": "one line, what this work item was",
  "subject": "2-4 words naming the part of the system touched",
  "summary": "3-6 sentences. What problem it addressed, what it did, how it ended.",
  "key_decisions": ["one line each; what was settled and why"],
  "supersedes": ["what this item explicitly replaced, retired, or deleted"],
  "status": "shipped | abandoned | superseded | unknown"
}
```

## Rules

- **Never guess the epic.** Use `"unknown"` unless the folder's own text names it. Do not infer
  from subject similarity to other folders. A wrong parent is worse than a missing one.
- `item_number` is `null` if not stated.
- `date_start`/`date_end`: use dates stated in the documents. The folder name's `YYYYMMDD` prefix
  is the archive date — use it for `date_end` if nothing better exists.
- `key_decisions` and `supersedes` are `[]` when the folder states none. Empty is a normal answer.
- `status`: only mark `shipped` if the folder says so. `unknown` is fine.
- Quote nothing at length. Every field is your own compressed prose.
- Valid JSON, one object per file, no markdown fences.

## Reference

Known epic names appear in these files in `.project/completed/` and `.project/backlog/`:
see `epic_files.txt` in the scratchpad. `completed/CHANGELOG.md` has entries for ~23 folders in
exactly this shape — consult it when a folder you were given appears there.

## Return

Reply with only: the count of files you wrote, and any folder you could not summarize with the reason.
