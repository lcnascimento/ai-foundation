# Principles ship as an always-on index plus on-demand references

Each plugin that owns Principles (`foundation`: 6, `engineering`: 19) ships one `principles` skill whose `references/<name>.md` hold the full texts, and a hook that injects a short index (one line per Principle, its upstream trigger `description`, plus the instruction to load it with `<plugin>:principles <name>` before applying it and to cite in the final reply each Principle that changed a decision) on `SessionStart` and `SubagentStart`. Each reference file is the Upstream `SKILL.md` copied byte for byte, provenance frontmatter included, so the texts stay Community and an update is a copy plus a sha bump.

A throwaway eval (`prototype/principles-delivery` branch, 6 Go scenarios with `claude -p`) settled it: the index with references loaded the expected Principle before the first edit in 6/6 tasks for +2k tokens at turn 1. One skill per Principle without an index cost the same context and recalled 2/6. Index plus one skill per Principle recalled 6/6 at twice the context. All texts as a Rule doesn't fit: 34k chars against the 10k `SessionStart` cap, which degrades to a 2k preview.

## Consequences

- Principles are not skills, so they don't spend the skill-listing budget and can't be auto-routed; the index is the only trigger.
- Custom skills reference a Principle by name and invocation (`apply prove-it-works: foundation:principles prove-it-works`), never by restating it. Community workflow skills stay unedited and rely on the index.
- The `principle-*` cross-references inside the Upstream texts (e.g. "see principle-build-the-lever") resolve through the index, not through skill names.
- The index is the only Rule in v1: plugins inject no other always-on text. Language, commit conventions and pointers to the Project setup are per-Project, so they live in the `CLAUDE.md` that Project setup writes (ADR-0007); autonomy is a Principle (ADR-0009); workflow stances such as "plan, don't do" stay in the skills that need them. A Rule with its own content must share the 10k `SessionStart` cap with the index.
- `foundation` started with 5 Community Principles; ADR-0009 added the Custom `know-when-to-stop`, making 6. A Custom Principle lives in the same `references/` and is listed in the same index, but carries no provenance frontmatter because it has no Upstream.
