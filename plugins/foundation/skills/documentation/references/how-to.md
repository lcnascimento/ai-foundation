# How-to

Steps to one goal for a reader who already knows the basics. It solves a problem a person has, not an operation the system can perform.

## Structure

```md
# How to {verb} {object}

{One sentence: the situation this solves and the result.}

## Before you start

{Prerequisites as a list: access, tools, state. Link the tutorial for readers new to the area.}

## Steps

1. {Command or action.}
2. {If the reader wants X, do Y; otherwise do Z.}

## Check the result

{The command or observation that proves it worked.}

## Troubleshooting

{Optional. One entry per known failure: the symptom, then the fix.}
```

## Rules

- Title by the task, "How to rotate the API key", never by the topic, "API keys".
- Lead with the problem. No preamble, no background: link the explanation instead.
- Numbered steps, one action each. Put the condition before the action: "If the build fails, run…".
- Forks are fine where the reader's situation differs: "If you use Docker, …".
- Cover the cases that happen, not every case. Completeness is reference's job.
- End on a check the reader can run, so they know they're done.
- Every command comes from the Project (its `Makefile`, scripts, CI) and was run when the environment allows.
