# Active Work

This folder contains work-in-progress item folders.

## Structure

```
active/
├── README.md           # This file
└── {item_name}/        # One folder per active work item
    ├── spec.md         # What needs to be done
    ├── design.md       # How to do it
    ├── plan.md         # Phased implementation plan
    └── [deliverables]  # Work products
```

## Starting a Work Item

1. Create folder: `mkdir {item_name}`
2. Create `spec.md` using `/spec` command or manually
3. Create `design.md` using `/design` command
4. Create `plan.md` with phased breakdown
5. Update `../CURRENT_WORK.md`

## During Work

1. Follow phases in `plan.md`
2. Check off completed tasks
3. Add notes and decisions

## Completing a Work Item

Follow [the project README's record-then-delete policy](../README.md#4-item-and-epic-close--the-standing-rule-owner-2026-08-23). Preserve durable decisions, promises, and useful findings in their owning registers or research. Remove the closed item folder and update CURRENT_WORK and BACKLOG; Git history is the archive.

## Naming Convention

Use descriptive, lowercase names with underscores:
- `user_auth_backend`
- `api_integration`
- `performance_optimization`

Avoid generic names like `task1` or `work`.
