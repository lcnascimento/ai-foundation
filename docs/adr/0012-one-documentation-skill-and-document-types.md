# One documentation skill writes every Document type, named the same everywhere

`foundation` ships one Custom skill, `documentation` (cited as `foundation:documentation`), that classifies, structures and writes any document of a Project into its docs backend (ADR-0005). It replaces the `doc-*` family planned in the v1 catalog. It lives in `foundation` because tutorials, how-tos, reference, explanations and decision records serve any domain. `technical-writing` (pstack) moves to `foundation` with it and stays an unedited Community skill for manual use.

The v1 Document types are `adr`, `tutorial`, `how-to`, `reference` and `explanation`. Each value is one name everywhere:

- in Linear, a child of the single-select workspace label group `document` (named without a prefix, per ADR-0003; written `document:<type>` in prose). An issue with it delivers exactly one document of that type and carries no `type` label. `to-tickets`, `triage` and the user apply it.
- in the repo, the directory `docs/<type>/` (singular, so `docs/tutorial/`, not `docs/tutorials/`).
- in Notion, one page with its own database per type, as ADR-0005 already lays out. The page name follows the Project language, and `domain.md` maps each type value to its database ID.

The skill's layout:

- `references/classify.md`: the classification tree, the per-type signals and red flags, and JTBD-first resolution, rewritten from nWave's `nw-divio-framework` (MIT, `metadata.upstreams`, ADR-0010).
- `references/<type>.md`: the structure of each type. `adr.md` is the former `ADR-FORMAT.md` of `domain-modeling`.
- `references/style.md`, derived from `technical-writing` and `unslop`, and `references/diagrams.md`, derived from `show-me`'s visual menu (Mermaid and trees only, no HTML file).

The skill carries these copies because `technical-writing`, `unslop` and `show-me` set `disable-model-invocation: true`, so no skill can load them through the Skill tool, and a Community skill can't drop the flag without becoming derived.

When a document is needed is decided while modeling, not while writing. `domain-modeling` keeps offering ADRs under its three criteria, also offers an `explanation` when a glossary term needs its why or history, and hands the writing to `foundation:documentation`. Other types come from the user or from an issue labelled `document:<type>`. In a wayfinder map, a ticket labelled `document:<type>` resolves by writing that document through the skill and linking it from the resolution comment. Project setup writes that rule into the Wayfinding operations section of `docs/agents/issue-tracker.md`, so `wayfinder` stays a Community skill.

A Domain plugin adds a type (for example `jtbd`) by shipping its own skill under the same contract and declaring the type to Project setup, which then creates the label and the Notion page. No v1 plugin adds one.

## Considered Options

- **Four skills, one per Divio quadrant**: rejected. They would share classification and backend writing, and four always-loaded descriptions would compete to trigger.
- **ADRs stay whole in `domain-modeling`**: rejected. The format and the backend writing move to the documentation skill. Only the decision to offer one stays in modeling.
- **Vendor `nw-divio-framework` as a Community skill**: rejected. Its two flags make it unreachable outside nWave's agents.
- **`humanizer` (blader) in place of `unslop`**: deferred. It handles process better (no invented facts, voice samples, when not to act), but it costs about 5x the tokens per use, and pstack skills cite `unslop` rule numbers. It stays a candidate replacement.
- **One Notion `Docs` database with a `Type` property**: rejected. The Unique ID prefix is per database, so ADRs would lose `ADR-` numbering, and types would lose their own properties (an ADR's status).
- **Wayfinder ignores `document:*`**: rejected in favor of the contract rule, so a map can plan a document as a ticket's deliverable.

## Consequences

- Amends ADR-0005: directories are singular, and `domain-modeling` and `improve-codebase-architecture` point to `foundation:documentation` instead of reading the backend themselves. They stay derived.
- Amends ADR-0003 (the `document` label group) and ADR-0007 (setup provisions labels and pages per enabled type, and writes the wayfinder rule).
- `style.md` and `diagrams.md` are derived copies, so an update to `technical-writing`, `unslop` or `show-me` is a manual merge.
- The `anthropic-skills:docs` description claims "any document", so `documentation`'s description must say it writes the Project's documents into the docs backend.
