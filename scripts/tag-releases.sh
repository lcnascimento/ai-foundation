#!/usr/bin/env bash
# Release tags (ADR-0006): create and push `<plugin>--v<X.Y.Z>` at HEAD for
# every plugin whose current version has no tag yet. Existing tags are left
# alone, so re-running on a commit without a bump does nothing.
#
# Run from the repository root.
# Usage: scripts/tag-releases.sh [remote]   (default: origin)
set -euo pipefail

remote="${1:-origin}"

git fetch --quiet --tags "$remote"

for manifest in plugins/*/.claude-plugin/plugin.json; do
  name="$(jq -r '.name' "$manifest")"
  version="$(jq -r '.version' "$manifest")"
  tag="$name--v$version"
  if git rev-parse --quiet --verify "refs/tags/$tag" >/dev/null; then
    echo "skip $tag: already exists"
    continue
  fi
  git tag -a "$tag" -m "$name $version"
  git push --quiet "$remote" "refs/tags/$tag"
  echo "tag  $tag"
done
