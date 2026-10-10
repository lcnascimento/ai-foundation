# One Linear workspace per Project, teams by domain

Each Project gets its own Linear workspace; inside it, a team per domain (`Engineering`/`ENG`, later Marketing, Business…) and Linear projects only for finite deliverables, optional and possibly cross-team (no catch-all project). A single shared workspace was rejected, whether split by a team per Project or by a team per domain plus a `repo` label group: a workspace per Project isolates data and MCP configuration, and no skill ever has to filter by Project to avoid crossing products.

All labels live at workspace level, lowercase:

- `type` (single-select): `bug`, `feature`, `improvement`, `chore`; other domains add their own values. mattpocock's `triage` category roles map `bug` → `bug`, `enhancement` → `feature`.
- `triage` (single-select): the five canonical state roles (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`), mapped 1:1 in `docs/agents/triage-labels.md`.
- `wayfinder:*`: flat prefixed labels, so the names skills filter by stay unambiguous.
- `document` (single-select): one child per Document type (`adr`, `tutorial`, `how-to`, `reference`, `explanation`); an issue that delivers a document carries it instead of `type` (ADR-0012).

## Considered Options

- **Triage roles as Linear statuses** (native Triage status for `needs-triage`, Canceled for `wontfix`): rejected because it splits one axis across two mechanisms and forces editing the vendored `triage` skill, which "applies labels". The single-select group enforces "exactly one state role" by itself. Linear's native Triage feature stays off.
- **SDLC phase as a label**: rejected; the workflow status carries it. The Engineering workflow is Backlog → Todo → In Progress → In Review → Done, plus Canceled and Duplicate.

## Consequences

- The official Linear MCP must target the right workspace per Project; Project setup owns that.
- Grouped label children are named without a prefix (`bug`, `ready-for-agent`); skill-owned namespaces use flat prefixed labels (`wayfinder:map`).
