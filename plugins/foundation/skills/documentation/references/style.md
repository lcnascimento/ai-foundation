# Style

Write so a tired engineer understands it on the first read. Derived from pstack's `technical-writing` (the sentence layers) and `unslop` (the AI-tell catalog, rule numbers kept). The type references own structure; this file owns sentences.

The rules are written for English. In another Project language, apply their intent (plain words, one meaning per word, active voice, no AI tells) with that language's own conventions.

## Above every rule

- **Cut every word that does no work.** "In order to" is "to". "It is important to note that" is nothing.
- **Use the short, everyday word.** "Use", not "utilize". "Help", not "facilitate".
- **The codebase is the word list.** Write the real symbol, file, flag or command, never a synonym or a description of it. Use the domain terms of `GLOSSARY.md` and none of the synonyms it lists under _Avoid_.
- **When a rule makes a sentence worse, fix the sentence another way.** The rules serve the reader.

## Rhythm and specifics

- Mix sentence lengths on purpose. Short sentences land a point. A longer one carries a fact with its condition or consequence.
- Be specific: not "schema changes can cause issues" but "a column rename fails the build".
- Have a view where the type allows it (explanation, an ADR's reasoning). Reference stays dry.
- Make every count, tree or path true at the commit that lands the document.

## Sentences to the reader

- Address the reader as "you", in the present tense. Name the actor: "the compiler checks", not "is checked".
- Instructions are commands: "Run `make test`." Never "should be run".
- Put the condition before the instruction: "To delete the record, run…". Put the common case first, exceptions after.
- No "please", and never "simply", "easy" or "quickly" in a procedure.
- Link text names the destination: the document's title or a short description. Never "click here".
- Headings state the point, in sentence case. A task heading is a bare verb phrase ("Create an instance"). One H1, no skipped levels.
- Numbered lists for sequences, bullets otherwise. Introduce a list with a full sentence and keep items parallel.
- Code, paths, flags and identifiers go in code font. UI labels go in bold.

## One reading only

- One instruction per sentence. Split instructions over about 20 words and other sentences over about 25.
- Keep the articles: "Remove the backup file", not "Remove backup file".
- Give each word one meaning, and each thing one name, everywhere in the document.
- Keep "only" and "not" next to the word they change.
- Break noun strings: "the script that checks the import budget", not "the import budget check script".
- Every "it", "they" and "this" points at one obvious noun. Repeat the noun when in doubt.
- Periods over semicolons. No slashes for "or": write "a, b, or both".
- No idioms, Latin abbreviations or "etc.": say up front that a list is partial.

## AI tells (`unslop`)

Scan the draft for each pattern and rewrite. The numbers are stable ids; gaps are intentional.

3. **Superficial -ing phrases**: "highlighting…", "ensuring…", "showcasing…". Delete, or state the fact.
5. **Vague attributions**: "experts believe". Name the source or delete.
7. **AI vocabulary**: additionally, crucial, delve, enhance, fostering, garner, interplay, intricate, landscape, pivotal, showcase, tapestry, testament, underscore, vibrant. Use the plain word.
8. **Fancy "is"**: "serves as", "stands as", "boasts", "features". Write "is" or "has".
9. **"Not just X, but Y."** State the point.
10. **Rule of three.** Use the natural number of items.
11. **Synonym cycling.** Pick one name and repeat it.
12. **False ranges**: "from X to Y" with no scale between them. List the items.
13. **Em dashes.** None. End the sentence or use a comma.
14. **Colons as connectors.** A colon introduces a list or an example, nothing else.
15. **Boldface overuse.** Bold only UI labels and the lead-in of a definition list.
16. **Inline-header lists**: "**Performance:** Performance improved…". Write prose, or a bold lead-in ending in a period followed by new detail.
17. **Title case headings.** Use sentence case.
18. **Decorative emojis.** Remove.
19. **Curly quotes.** Use straight quotes.
20. **Chatbot phrases**: "I hope this helps", "Certainly!". Remove.
22. **Sycophancy.** Respond directly.
23. **Filler**: "due to the fact that" is "because".
24. **Hedging stacks**: "could potentially possibly" is "may".
25. **Generic conclusions**: "the future looks bright". State a fact or a plan, or end.
26. **Abstract metaphor nouns**: substrate, wedge, vector, locus, nexus, primitive, harness, surface, bedrock, scaffolding, paradigm, ratchet, endgame, north star, flywheel. Use the concrete word.
27. **Feelings instead of mechanisms**: "SQL you can read" becomes "`.toSQL()` returns the exact query". A sentence that could appear unchanged in another project's docs says nothing about this one. Cut it.
28. **Dense sentences.** If the reader must backtrack, split it.
29. **Passive voice.** Name the actor unless it is unknown or irrelevant.
30. **Adverbs propping weak verbs**: "significantly improves" becomes the measured delta.
31. **Fancy words**: utilize, leverage, facilitate, numerous, in the event that. Use, use, help, many, if.
32. **Mannered prose**: aphorisms, personified code, figurative verbs ("rides along"). Say it literally.
33. **Over-compression**: dropped articles, arrows, symbol-speak. Write whole sentences.

## Checklist

Before storing the document, confirm:

- [ ] Every name, command and number comes from the source.
- [ ] No sentence mixes in another type's job (no tutorial hand-holding in reference, no arguing in a how-to).
- [ ] No AI tell from the list above survives.
- [ ] Each thing has one name throughout, matching `GLOSSARY.md`.
- [ ] Headings state points, in sentence case.
