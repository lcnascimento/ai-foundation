# Classify a document

Every document serves one reader job. Find the job, and the type follows. Rewritten from nWave's `nw-divio-framework`, with `adr` added.

## Decision tree

Ask about the reader, not the content:

1. Does the reader need to know that a decision was made and why, so nobody reverses it by accident? → `adr`
2. Is the reader learning this for the first time? → `tutorial`
3. Is the reader trying to get one task done?
   - and already knows the basics → `how-to`
   - and doesn't → `tutorial`
4. Is the reader looking up one specific fact (a flag, a field, an error, an endpoint)? → `reference`
5. Is the reader trying to understand why something is the way it is? → `explanation`
6. None of the above: the content needs restructuring before it has a type. Restate the reader's job with the user.

`adr` and `explanation` sit close. An ADR records one decision at the moment it's made, short and dated. An explanation teaches a topic (how the parts fit, its history, the trade-offs across several decisions) and gets updated as the topic moves. An explanation links the ADRs it draws on.

## The four reading quadrants

```
             PRACTICAL      THEORETICAL
STUDYING     tutorial       explanation
WORKING      how-to         reference
```

Neighbours get confused: tutorial and how-to both have steps (they differ in assumed knowledge), how-to and reference are both used at work, reference and explanation both hold knowledge, explanation and tutorial are both read while studying.

## Signals per type

| Type | Signals | Red flags (it's another type) |
| - | - | - |
| `adr` | "We decided", "instead of", rejected alternatives, hard to reverse | Steps to follow; a whole topic's background |
| `tutorial` | "Getting started", "your first…", no prerequisites, "step 1, step 2", "you should see…" | "Assumes you know…", "if you need to…", "for advanced users" |
| `how-to` | "How to <verb>", prerequisites, steps, a done condition | "Let's first understand what X is" |
| `reference` | Tables of fields, flags, parameters, returns, errors | "You might want to…", opinions, a conversational tone |
| `explanation` | "Why", background, architecture, design trade-offs, history | Numbered steps, "do this:", API details |

## Resolve with the job-to-be-done

When the tree is ambiguous, or a choice inside a type has two plausible answers (ordering, one section or three, prose or table, scratch data or real data), don't pick by taste. Return to the document's job and let the answer fall out.

Each type's canonical job:

| Type | Job | Constraints it implies |
| - | - | - |
| `adr` | "Tell me what was decided and why, so I don't undo it." | Short, dated, one decision, the alternatives that lost |
| `tutorial` | "Build my mental model of X by doing it once, end to end, without risking my real project state." | Reproducible, safe, self-contained, cause and effect visible |
| `how-to` | "Fix this specific situation now; don't teach me fundamentals." | Problem first, decision points, no preamble, link to the tutorial for newcomers |
| `reference` | "Give me one specific answer." | Ctrl-F friendly, dense, systematic order, no narrative, one heading per lookup category |
| `explanation` | "Help me understand the design so I can extend or critique it." | Discursive, links to evidence (ADRs, incidents, benchmarks), no instructions |

To resolve a choice:

1. Restate the document's job in one sentence, starting from the canonical one and narrowing it to this document.
2. List the concrete constraints that sentence implies.
3. Score each option against the constraints.
4. Pick the option that meets the most. On a tie, pick the one that breaks the fewest.

Example: a reference page has three short sections. Fold them into one "Notes" section? The job is "one specific answer", so ctrl-F friendly, so three headings are three landing points. Keep them separate.

## Split blended documents

A document carrying two canonical jobs in tension ("a tutorial that is also the reference") serves neither. When you find two jobs, write two documents of their own types and link them.
