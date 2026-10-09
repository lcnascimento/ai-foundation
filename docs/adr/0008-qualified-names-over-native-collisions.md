# Skills that invoke a skill shadowed by a native command cite its plugin-qualified name

Claude Code ships a native `/code-review` (correctness bugs in the diff) that shares its name with mattpocock's `code-review` (Standards + Spec axes), which `engineering` vendors as `engineering:code-review`. `implement` and `implement-spec` end by running "`code-review`", so an agent following them can route to the native command and skip the Standards and Spec review the workflow depends on. We derive both skills, and any future Community skill that invokes a skill whose name collides with a native command, with one edit: cite the plugin-qualified name (`engineering:code-review`). Making the edit turns them into derived Custom skills (`metadata.status: derived`, ADR-0001).

## Considered Options

- **Document the ambiguity and accept it**: rejected. The failure is silent, and the review step is the one that catches spec drift in AFK runs.
- **Have setup write a disambiguation line in the `## Agent skills` block** (ADR-0002, ADR-0007) and keep `implement*` Community: rejected. It depends on the model reading `CLAUDE.md` correctly at the moment it resolves the skill, while the qualified name in the skill text resolves deterministically.

## Consequences

- `implement` and `implement-spec` need a manual merge on every upstream update, like any derived skill.
- Native commands are part of the v1 review layer without being vendored: `/code-review` (bugs), `/security-review` and `/simplify`, alongside `engineering:code-review` (conformance).
- Prose mentions that don't invoke the skill (e.g. `tdd` sending refactors to the review stage) don't trigger a derivation.
