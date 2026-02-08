---
date: 2026-02-06T14:00:00-06:00
researcher: Claude
topic: "PreToolUse hook for automated common-sense approvals across 1cfe repos"
tags: [research, hooks, developer-experience, automation]
status: complete
last_updated: 2026-02-06
---

# Research: PreToolUse Hook for Automated Common-Sense Approvals

**Date**: 2026-02-06
**Researcher**: Claude
**Research Type**: Architecture / Developer Experience

## Research Question

Design a PreToolUse hook strategy that auto-approves common-sense operations across all `~/1cfe/` repos and `/tmp/`, while blocking dangerous commands (rm -rf outside /tmp, git commit, git push). Must handle compound `&&` commands by checking each piece separately.

## Summary

- **PreToolUse hooks** receive JSON on stdin with `tool_name` and `tool_input`, and can return `permissionDecision: "allow"|"deny"|"ask"` to control approval
- A **command hook** (bash script) is the right choice here: deterministic, fast (~5ms), no LLM latency
- Compound commands (`&&`, `||`, `;`) can be split with `IFS` or regex and each segment checked independently
- The hook should go in **global settings** (`~/.claude/settings.json`) since it covers all repos under `~/1cfe/`
- Three matchers needed: one for `Bash`, one for `Read|Write|Edit|Glob|Grep`, and one for `Task|NotebookEdit` (if desired)

## Detailed Findings

### Hook API for PreToolUse

**Input JSON** (received on stdin):
```json
{
  "session_id": "abc123",
  "cwd": "/home/reid/1cfe/sysml-codegen",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "cd /home/reid/1cfe/literature && cp /tmp/file.md .",
    "description": "Copy file",
    "timeout": 120000
  }
}
```

For file tools (Read/Write/Edit/Glob/Grep), `tool_input` contains:
- `file_path` (Read, Write, Edit)
- `pattern` + optional `path` (Glob, Grep)

**Output to approve** (exit 0):
```json
{"hookSpecificOutput": {"permissionDecision": "allow"}}
```
Or simply `exit 0` with no output (also approves).

**Output to deny** (exit 2, on stderr):
```json
{"hookSpecificOutput": {"permissionDecision": "deny"}, "systemMessage": "Reason here"}
```

**Output to defer to user** (exit 2, on stderr):
```json
{"hookSpecificOutput": {"permissionDecision": "ask"}, "systemMessage": "Reason here"}
```

### Compound Command Splitting Strategy

The key insight: Claude Code often chains commands with `&&`. We need to split on `&&`, `||`, and `;` and check each segment.

**Approach**: Use bash string splitting with regex, being careful about:
- Quoted strings containing `&&` (rare but possible)
- Subshells `$()` and backticks (treat as opaque)
- Pipes `|` (not a command separator, left side feeds right side)

**Pragmatic approach**: Split on ` && `, ` || `, and ` ; ` (with surrounding spaces), then check each segment. This handles 99% of real-world Claude commands. Edge cases with quoted separators are unlikely in practice.

```bash
# Split compound command into segments
IFS=$'\n' read -r -d '' -a segments < <(
  echo "$command" | sed 's/ && /\n/g; s/ || /\n/g; s/ ; /\n/g' && printf '\0'
)
```

### What to Check Per Segment

For each command segment, extract the base command and check:

1. **`cd`** - Always safe (just changes directory)
2. **`cp`, `mv`, `mkdir`, `touch`, `ls`, `cat`, `head`, `tail`** - Safe if paths are in allowed zones
3. **`uv run python`**, **`uv run pytest`**, **`uv run mypy`**, **`uv run ruff`** - Safe (our dev tools)
4. **`uv run sysml-codegen`**, **`uv run agentic-mbse`** - Safe (our packages)
5. **`which`, `claude`, `echo`, `date`, `pwd`, `whoami`** - Always safe
6. **Custom scripts from `.claude/` or `.project/`** - Safe (e.g., `get-metadata.sh`)
7. **`git status`, `git diff`, `git log`, `git branch`** - Safe (read-only git)
8. **`rm -rf`** - Only safe in `/tmp/`
9. **`git commit`, `git push`, `git commit --amend`** - Always ask user
10. **`ruff`, `black`, `isort`** - Safe (formatters)

### Path Validation

For file tools, validate that paths resolve within allowed zones:

```bash
ALLOWED_PATHS=(
  "/home/reid/1cfe"
  "/tmp"
  "/home/reid/agentic-project-init"  # optional: your plugin/pack source
)
```

Use `realpath` to resolve symlinks and `..` traversal before checking.

### Existing Infrastructure

**Current global settings** (`~/.claude/settings.json`):
```json
{
  "hooks": {
    "PreCompact": [{ "matcher": "auto", "hooks": [{"type": "command", "command": "..."}] }]
  }
}
```
We would add `PreToolUse` entries alongside the existing `PreCompact`.

**Existing hooks in the ecosystem**:
- `ruff-format.sh` (PostToolUse) - Good pattern reference for JSON parsing
- `precompact-capture.sh` (PreCompact) - Good pattern for delegation
- `validate-bash.sh` (example) - Good pattern for command checking

**Custom scripts to whitelist** (found across repos):
- `get-metadata.sh` (in `.project/scripts/` of multiple repos)
- `get_metadata.sh` (in teax/thoughts/commands/)
- `init_agent_prompts.sh`
- `run_manual_extractions.sh`
- `setup-docling.sh`
- `replicate_setup.sh`
- Various `ruff-format.sh` hooks

### Configuration Location Decision

| Option | Pros | Cons |
|--------|------|------|
| Global `~/.claude/settings.json` | One config for all repos | Can't customize per-repo |
| Per-repo `.claude/settings.json` | Repo-specific rules | Must duplicate across all repos |
| Global script, per-repo config | Best of both worlds | More complex |

**Recommendation**: Global hook script at `~/.claude/hooks/auto-approve.sh`, configured in `~/.claude/settings.json`. The script itself can be smart about context.

## Architecture: Proposed Hook Design

### Two-Matcher Strategy

```json
{
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "/home/reid/.claude/hooks/auto-approve.sh",
          "timeout": 5
        }
      ]
    },
    {
      "matcher": "Read|Write|Edit|Glob|Grep",
      "hooks": [
        {
          "type": "command",
          "command": "/home/reid/.claude/hooks/auto-approve.sh",
          "timeout": 5
        }
      ]
    }
  ]
}
```

Same script handles both - it reads `tool_name` from stdin JSON and branches accordingly.

### Script Logic Flow

```
auto-approve.sh
  |
  ├── tool_name == "Bash"
  │   ├── Split command on && / || / ;
  │   ├── For each segment:
  │   │   ├── Extract base_cmd (first word after cd/env/etc.)
  │   │   ├── Is it a BLOCKED command? → deny/ask
  │   │   ├── Is it in ALWAYS_SAFE list? → continue
  │   │   ├── Is it a uv/python/project command? → continue
  │   │   ├── Does it reference only allowed paths? → continue
  │   │   └── Unknown? → exit 0 (fall through to normal permission flow)
  │   └── All segments passed → allow
  │
  ├── tool_name == "Read|Write|Edit"
  │   ├── Extract file_path from tool_input
  │   ├── Resolve with realpath
  │   ├── Under ~/1cfe/ or /tmp/? → allow
  │   └── Otherwise → fall through (don't deny, just don't auto-approve)
  │
  └── tool_name == "Glob|Grep"
      ├── Extract path from tool_input
      ├── Under ~/1cfe/ or /tmp/ (or no path = cwd)? → allow
      └── Otherwise → fall through
```

**Key design choice**: The hook should only emit `permissionDecision: "allow"` or `permissionDecision: "deny"` for things it's certain about. For anything ambiguous, `exit 0` with no output lets the normal permission flow handle it (user gets prompted as usual).

### Blocked vs. Ask vs. Allow

| Command Pattern | Decision | Rationale |
|----------------|----------|-----------|
| `rm -rf` outside `/tmp/` | **deny** | Destructive, never auto-approve |
| `rm -rf` in `/tmp/` | **allow** | Temp files, safe to clean |
| `git commit`, `git push` | **ask** | User should always confirm |
| `git add` | **ask** | Staging is a commit precursor |
| `cd`, `ls`, `pwd`, `echo`, `which` | **allow** | Zero risk |
| `cp`, `mv`, `mkdir` in allowed paths | **allow** | Safe file ops |
| `uv run *` | **allow** | Dev tooling |
| `python`, `python3` | **allow** | Script execution |
| `ruff`, `mypy`, `pytest` | **allow** | Dev tools |
| Custom `.sh` scripts in project dirs | **allow** | Our scripts |
| Unknown commands | **(no decision)** | Fall through to user prompt |

## Code References

- `~/.claude/settings.json` - Global hook config location
- `~/.claude/hooks/precompact-capture.sh` - Existing hook pattern
- `~/1cfe/agentic-mbse/.claude/hooks/ruff-format.sh:1-25` - JSON parsing pattern
- Plugin hook docs: `~/.claude/plugins/.../plugin-dev/skills/hook-development/SKILL.md`
- Example validate-bash: `~/.claude/plugins/.../hook-development/examples/validate-bash.sh`
- Example validate-write: `~/.claude/plugins/.../hook-development/examples/validate-write.sh`

## Feasibility Assessment

**Fully feasible.** The PreToolUse hook API supports exactly this use case:
- `permissionDecision: "allow"` auto-approves without user prompt
- `permissionDecision: "deny"` blocks without user prompt
- `permissionDecision: "ask"` shows the normal user prompt
- A simple bash script with `jq` can handle all the logic in <5ms
- Compound command splitting is straightforward for practical cases

**Risk**: Over-aggressive auto-approval could allow unintended operations. Mitigation: start conservative (allow-list approach), log decisions to a file for auditing, expand the allow-list over time.

## Recommendations

### Implementation Plan

1. **Create `~/.claude/hooks/auto-approve.sh`** - Single script handling both Bash and file tools
2. **Add PreToolUse config to `~/.claude/settings.json`** - Two matchers (Bash + file tools)
3. **Add a debug/audit log** - Write decisions to `/tmp/claude-hook-audit.log` during initial testing
4. **Test with `claude --debug`** - Verify hooks fire and decisions are correct
5. **Iterate on the allow-list** - Add commands as you encounter annoying prompts

### Key Implementation Details

- Use `set -euo pipefail` for safety
- Parse with `jq` (already available)
- Use `realpath --relative-to` for path checking
- Keep the script fast (<10ms) - avoid subshells where possible
- For compound commands, a simple `sed` split is sufficient - no need for a full shell parser
- Default to "no decision" (exit 0, no output) for anything uncertain - this preserves the normal permission prompt as a safety net

### What NOT to Do

- Don't use a prompt-based hook here - adds 2-5s latency per tool call for something that should be deterministic
- Don't try to parse all shell syntax (pipes, subshells, heredocs) - just handle `&&`/`||`/`;`
- Don't auto-approve `git` write operations even if they seem safe - the user wants explicit control

## Open Questions

1. **Should `git add` be auto-denied or deferred to ask?** - It's not destructive but is a precursor to commit
2. **Should the hook also cover `~/agentic-project-init/`?** - The plugin/pack source directory
3. **Should there be a per-repo override mechanism?** - e.g., a `.claude/auto-approve.json` that adds repo-specific allowed commands
4. **Audit logging**: Keep permanently or just during testing?
