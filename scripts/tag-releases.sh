#!/usr/bin/env bash
# Release tags (ADR-0006): create and push `<plugin>--v<X.Y.Z>` at HEAD for
# every plugin whose current version has no tag on the remote yet. The remote
# is the source of truth: a tag that exists only locally (an earlier push
# failed) is pushed as is, and a tag already on the remote is left alone, so
# re-running on a commit without a bump does nothing.
#
# Run from the repository root.
# Usage: scripts/tag-releases.sh [remote]   (default: origin)
set -euo pipefail

remote="${1:-origin}"

git fetch --quiet --tags "$remote"
remote_tags="$(git ls-remote --tags --refs "$remote" | awk '{print $2}')"

for manifest in plugins/*/.claude-plugin/plugin.json; do
  name="$(jq -r '.name' "$manifest")"
  version="$(jq -r '.version' "$manifest")"
  tag="$name--v$version"
  if grep -qxF "refs/tags/$tag" <<<"$remote_tags"; then
    echo "skip $tag: already on $remote"
    continue
  fi
  if git rev-parse --quiet --verify "refs/tags/$tag" >/dev/null; then
    echo "push $tag: exists locally but not on $remote"
  else
    git tag -a "$tag" -m "$name $version"
    echo "tag  $tag"
  fi
  git push --quiet "$remote" "refs/tags/$tag"
done
