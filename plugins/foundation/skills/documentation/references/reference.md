# Reference

Facts for lookup. The reader knows what they're looking for and wants the answer fast.

## Structure

Mirror the structure of the thing described, so the reader can move between the code and the document. A typical page:

```md
# {Name of the thing: the module, CLI, API, config file}

{One sentence: what it is. Link the explanation for the why.}

## {Lookup category, e.g. Flags, Endpoints, Fields, Errors, Environment variables}

| Name | Type | Default | Description |
| - | - | - | - |
| `--port` | int | `8080` | Port the server listens on. |

## {Next category}
```

## Rules

- Describe, only. No instructions, no persuasion, no opinion, no narrative.
- One heading per lookup category, so each is a landing point for ctrl-F. Don't fold short categories together.
- Order entries systematically: by the code's order when it has a meaningful one, otherwise alphabetically.
- Be complete within the scope you state, and state the scope: "every flag of `cli serve`".
- State limits, defaults, errors and units with no hedging.
- Names are exact: the real symbol, flag, field or error text, in code font.
- When the source can generate the content (OpenAPI, `--help`, schema files), point at the generated source or generate from it, so the page can't drift.
- A short usage example per entry is fine when it shows syntax. A walkthrough is a how-to.
