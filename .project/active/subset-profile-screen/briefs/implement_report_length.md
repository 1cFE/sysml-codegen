Orchestrator ruling on report length (execution detail; display only, no outcome changes). Spec says `generate` and `check` report findings "in the same form", so the rule applies to both commands' shared `log_report`:
- Print in full, with location and remedy: refused findings, `candidate_refusal` findings, unconfirmed findings, unverified checks / not-assessed entries, and disagreements. These are what a modeler must act on or what blocks readiness.
- Print admitted findings as a single count line.
- Print omitted and excluded findings as one line per rule (rule ID, outcome, count, and the remedy once), not one line per finding.
- No new flag. A modeler who wants every finding uses L6's structured output; say so in the summary line if it's cheap.
Record this as an orchestrator decision in the design (D5) and the plan notes, add a test pinning the shape, keep 0 record/byte differences, commit as a follow-up to Phase 8, and report the catf_mfe line count after.
