# PROTOTYPE: Principle delivery (AI-11)

Throwaway eval for the question in AI-11: how do curated Principles reach the agent without bloating context?
Nothing here is production; the validated decision is recorded on the Linear ticket.

- `build.sh <pstack-checkout>` builds four throwaway plugins from pstack's 24 `principle-*` skills (`backnotprop/pstack` @ `3a60467`) into `variants/` (not committed: regenerate):
  - **a-index-references**: always-on index Rule (SessionStart hook, one line per Principle = upstream `description`) + one `principles` skill whose `references/<name>.md` hold the full texts, loaded with `principles <name>`.
  - **b-skill-per-principle**: 24 model-invocable skills, no index (routing by description only).
  - **c-index-skills**: the same index + 24 model-invocable skills (pstack's `poteto-mode` index, made always-on).
  - **d-all-rules**: all 24 full texts as one always-on Rule.
- `run.sh <runs-dir>` runs `scenarios.tsv` (6 tasks on the Go `fixture/`, each with one expected Principle, plus 1 control) against every variant and a no-plugin baseline (`0-none`) with `claude -p` (Claude Code 2.1.286, default model).
- `analyze.py <runs-dir> scenarios.tsv` grades the transcripts. Raw transcripts of the run reported below are in `runs/`.

## Results (1 run per cell, 2026-10-08)

| variant | expected loaded | before 1st edit | expected cited | loads/run | control loads | ctx at turn 1 (Δ vs none) | cost |
|---|---|---|---|---|---|---|---|
| 0-none | 0/6 | 0/6 | 0/6 | 0.0 | 0 | 17362 (+0) | $1.17 |
| a-index-references | 6/6 | 6/6 | 6/6 | 1.0 | 0 | 19380 (+2018) | $1.54 |
| b-skill-per-principle | 2/6 | 2/6 | 0/6 | 0.3 | 0 | 19371 (+2009) | $1.50 |
| c-index-skills | 6/6 | 6/6 | 6/6 | 1.2 | 0 | 21320 (+3958) | $1.69 |
| d-all-rules | 0/6 | 0/6 | 2/6 | 0.0 | 0 | 18259 (+897) | $1.59 |

Notes:

- **D doesn't fit**: full texts are 34k chars against SessionStart's 10k cap, so Claude Code persisted them to a file and injected a 2k-char preview (hence the small Δ). The agent cited names from the preview without reading the texts.
- **B pays the same context as A** (24 descriptions in the skill listing, which also competes for the ~1% listing budget) but recalls 2/6 and never cites.
- **C = A on recall** at twice the context (index + 24 listing entries).
- **Loading changes the outcome**: in s6 (the "4x faster" PR description) A reran the benchmark, found it ~4% *slower*, and kept the claim out of the PR; the baseline wrote "4x faster" and listed caveats after it.
- **Caveats**: n=1 per cell; edits made via Bash are detected by regex; the citation instruction exists only in variants with an index (A, C, D); subagents were not tested (SessionStart doesn't reach them).
