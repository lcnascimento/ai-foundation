# Tutorial

A lesson. The reader builds something once, end to end, and leaves with a working mental model and the confidence to go on. You are the teacher, and the learner's success is your job.

## Structure

```md
# {What the reader builds, as a noun phrase}

{One or two sentences: what they will have at the end, and roughly how long it takes.}

## Before you start

{What to install or have, with versions. Prefer "nothing" for a first tutorial.}

## Step 1: {bare verb phrase}

{One action per step.}

{Expected output, in a code block.}

## Step 2: …

## What you built

{Two or three sentences naming what now works, then links: the how-tos for real tasks, the explanation for the why.}
```

## Rules

- Open with what the reader builds, not what they will "learn".
- Every step produces a visible result. Show what they should see: the output, the log line, the page.
- Work in a scratch directory or sandbox, never in the reader's real project state.
- Run every step yourself when the environment allows, and paste the real output.
- One path only. No options, no "alternatively", no branches.
- Explanation shrinks to one clause and a link. A teaching pause breaks the lesson.
- Write as "we" and in commands: "First, create the file. Now, run the server."
- Reference tables and edge cases belong in other documents. Link them at the end.
