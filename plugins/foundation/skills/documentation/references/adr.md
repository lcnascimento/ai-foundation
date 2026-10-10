# ADR

An architecture decision record captures that a decision was made, and why. Formerly mattpocock's `domain-modeling/ADR-FORMAT.md`; where ADRs live comes from the docs backend (SKILL.md), not from this file.

## Template

```md
# {Short title of the decision}

{1-3 sentences: what's the context, what did we decide, and why.}
```

That's it. An ADR can be a single paragraph. The value is in recording *that* a decision was made and *why*, not in filling out sections.

## Optional sections

Include these only when they add real value. Most ADRs won't need them.

- **Status** (`proposed | accepted | deprecated | superseded by ADR-NNNN`): when decisions get revisited. In the repo it is frontmatter; in Notion, the database's status property when it has one.
- **Considered Options**: only when the rejected alternatives are worth remembering.
- **Consequences**: only when non-obvious downstream effects need calling out. An ADR that amends an earlier one says so here and names it.

## Numbering

- **Repo**: sequential, `0001-slug.md`, `0002-slug.md`. Scan the ADR directory for the highest number and add one. Create the directory with the first ADR.
- **Notion**: the database's Unique ID property assigns `ADR-N`. Never number by hand.

An ADR is immutable once accepted. A changed decision gets a new ADR that supersedes or amends the old one, and the old one's status points at it.

## Is it an ADR?

All three must be true:

1. **Hard to reverse**: changing your mind later costs something real.
2. **Surprising without context**: a future reader will look at the code and wonder "why on earth did they do it this way?"
3. **The result of a real trade-off**: there were genuine alternatives and you picked one for specific reasons.

When one fails, it's not an ADR: an easy-to-reverse decision just gets reversed, an unsurprising one raises no question, and one with no alternative records only "we did the obvious thing". The background of a topic is an `explanation`.

What qualifies:

- **Architectural shape.** "We're using a monorepo." "The write model is event-sourced, the read model is projected into Postgres."
- **Integration patterns between contexts.** "Ordering and Billing communicate via domain events, not synchronous HTTP."
- **Technology choices that carry lock-in.** Database, message bus, auth provider, deployment target. Only the ones that would take a quarter to swap out.
- **Boundary and scope decisions.** "Customer data is owned by the Customer context; other contexts reference it by ID only." The explicit no-s are as valuable as the yes-s.
- **Deliberate deviations from the obvious path.** "We're using manual SQL instead of an ORM because X." These stop the next engineer from "fixing" something that was deliberate.
- **Constraints not visible in the code.** "We can't use AWS because of compliance requirements." "Response times must be under 200ms because of the partner API contract."
- **Rejected alternatives when the rejection is non-obvious.** If you considered GraphQL and picked REST for subtle reasons, record it, or someone will suggest GraphQL again in six months.
