# GitHub commands

Run them from the worktree; outside the repo, set `GH_HOST` as `docs/agents/forge.md` says. `<owner>`, `<repo>` and `<number>` come from step 1.

## Step 1

```bash
gh pr view --json number,url,headRefName,headRefOid,isDraft,body
gh api user --jq .login    # your login, to tell your comments from the reviewers'
```

## Step 2

Checks on the head commit, then the logs of a failed run:

```bash
gh pr checks --json name,state,bucket,link,workflow
gh run view <run-id> --log-failed
```

A Sonar check is a check run of the Sonar app, with no workflow run behind it, so it has no logs to read and no job to rerun; its summary carries the quality gate verdict and the new issues:

```bash
gh api "repos/<owner>/<repo>/commits/<sha>/check-runs" \
  --jq '.check_runs[] | select(.name | test("sonar"; "i")) | {name, conclusion, summary: .output.summary, text: .output.text}'
```

The time of the last push, the earliest check suite created on the head commit (`<sha>` is `headRefOid`), from any app:

```bash
gh api "repos/<owner>/<repo>/commits/<sha>/check-suites" --jq '[.check_suites[].created_at] | min'
```

Review threads, PR comments, review bodies and the head commit's date, the fallback when the head commit has no check suite, in one query:

```bash
gh api graphql -F owner=<owner> -F repo=<repo> -F number=<number> -f query='
query($owner:String!, $repo:String!, $number:Int!) {
  repository(owner:$owner, name:$repo) {
    pullRequest(number:$number) {
      commits(last:1) { nodes { commit { oid committedDate } } }
      reviewThreads(first:100) { nodes {
        id isResolved isOutdated path line
        comments(first:50) { nodes { author { login } body createdAt url } }
      } }
      comments(last:100) { nodes { author { login } body createdAt url } }
      reviews(last:100) { nodes { author { login } body state submittedAt url } }
    }
  }
}'
```

An item is a thread with `isResolved: false` whose last comment's author is not your login, and a comment or a non-empty review body by someone else with `createdAt`/`submittedAt` after the last push.

## Step 5

```bash
gh run list --commit <sha> --json databaseId,createdAt,status,conclusion
gh pr checks --watch
gh run rerun <run-id> --failed
```

## Step 6

Reply in a thread, with the thread `id` from step 2. Nothing here resolves it:

```bash
gh api graphql -f threadId=<thread-id> -f body="<reply>" -f query='
mutation($threadId:ID!, $body:String!) {
  addPullRequestReviewThreadReply(input:{pullRequestReviewThreadId:$threadId, body:$body}) { comment { url } }
}'
```

Answer the PR comments and review bodies:

```bash
gh pr comment <number> --body-file <file>
```
