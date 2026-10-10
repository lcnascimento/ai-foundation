# Explanation

Understanding. The reader steps away from the keyboard to learn why the system is the way it is, so they can extend or critique it.

## Structure

```md
# {Topic, a title that reads well after an implicit "About"}

{The why question this answers, in one or two sentences.}

## {Heading that states a point, e.g. "Orders are events because billing replays them"}

{Context, reasoning, history, constraints.}

## {Alternatives and trade-offs}

{What else was possible and what made the difference.}

## Further reading

{The ADRs, incidents, benchmarks or code this draws on.}
```

## Rules

- One bounded topic, readable away from the code.
- Anchor on a real why question a reader has asked or will ask.
- Give context: design decisions, history, constraints, alternatives. Link the evidence (ADRs, incidents, benchmarks) rather than asserting it.
- Opinion is allowed here and nowhere else. Weigh the trade-offs and say what you make of them.
- No instructions, no command walkthroughs, no API tables. Link the how-to and the reference.
- When the topic is one decision, it's an ADR. When it spans several, the explanation tells the story and links each ADR.
- Diagrams earn their place here: architecture, data flow, a sequence across components (see diagrams.md).
- A glossary term that needs its why or history gets an explanation, linked from its `GLOSSARY.md` entry. The definition itself stays in the glossary.
