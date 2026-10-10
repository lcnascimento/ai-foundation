#!/usr/bin/env bash
# Tests for scripts/check-provenance.py against throwaway fixture repos, offline
# (PROVENANCE_UPSTREAM_DIR stands in for raw.githubusercontent.com).
#
# Usage: tests/check-provenance.test.sh
# Needs: bash, python3 with PyYAML.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
check="$repo/scripts/check-provenance.py"
sha=1111111111111111111111111111111111111111
sha2=2222222222222222222222222222222222222222
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

upstream_text='---
name: principle-sample
description: "Apply when testing."
disable-model-invocation: true
---

# Sample

Body copied from the Upstream.
'

# fixture <dir>: a valid repo with one Community reference (single form),
# one derived skill (list form) and one Custom skill (no provenance).
fixture() {
  local d="$1"
  mkdir -p "$d/upstream/acme/principles/$sha/skills/principle-sample" \
    "$d/plugins/p/skills/principles/references" "$d/plugins/p/skills/principles/licenses" \
    "$d/plugins/p/skills/stack/licenses" "$d/plugins/p/skills/custom"
  printf '%s' "$upstream_text" > "$d/upstream/acme/principles/$sha/skills/principle-sample/SKILL.md"
  echo "MIT License" > "$d/plugins/p/skills/principles/licenses/acme-principles"
  cat > "$d/plugins/p/skills/principles/references/sample.md" <<EOF
---
name: principle-sample
description: "Apply when testing."
disable-model-invocation: true
license: MIT
metadata:
  upstream: acme/principles
  path: skills/principle-sample/SKILL.md
  sha: $sha
  status: community
---

# Sample

Body copied from the Upstream.
EOF
  cat > "$d/plugins/p/skills/stack/SKILL.md" <<EOF
---
name: stack
description: House stack rules.
license: MIT AND Apache-2.0
metadata:
  status: derived
  upstreams:
    - repo: acme/go-skills
      sha: $sha
      path: skills/
      license: MIT
    - repo: https://github.com/other/ts-rules
      sha: $sha2
      path: rules/typescript.md
      license: Apache-2.0
---

Rewritten content.
EOF
  echo "MIT License" > "$d/plugins/p/skills/stack/licenses/acme-go-skills"
  echo "Apache License" > "$d/plugins/p/skills/stack/licenses/other-ts-rules"
  printf -- '---\nname: custom\ndescription: Ours.\n---\n\nOurs.\n' > "$d/plugins/p/skills/custom/SKILL.md"
}

pass=0
fail=0
# case <name> <expect: ok|fail> <expected stderr substring or ""> <mutation>
case_() {
  local name="$1" expect="$2" needle="$3" mutation="$4"
  local d="$tmp/$pass-$fail-${name// /-}"
  fixture "$d"
  (cd "$d" && eval "$mutation")
  local status=0
  PROVENANCE_UPSTREAM_DIR="$d/upstream" python3 "$check" "$d" >"$d.out" 2>"$d.err" || status=$?
  local ok=1
  if [ "$expect" = ok ]; then
    [ "$status" -eq 0 ] || ok=0
  else
    [ "$status" -eq 1 ] && grep -qF -- "$needle" "$d.err" || ok=0
  fi
  if [ "$ok" -eq 1 ]; then
    echo "ok: $name"
    pass=$((pass + 1))
  else
    echo "FAIL: $name (exit $status)" >&2
    cat "$d.out" "$d.err" >&2
    fail=$((fail + 1))
  fi
}

ref=plugins/p/skills/principles/references/sample.md
stack=plugins/p/skills/stack/SKILL.md

case_ "valid fixture passes (single and list forms)" ok "" ":"
case_ "Community body diverges from Upstream" fail "differs from Upstream" \
  "sed -i.bak 's/Body copied/Body edited/' $ref"
case_ "Community frontmatter diverges from Upstream" fail "differs from Upstream" \
  "sed -i.bak 's/Apply when testing./Apply always./' $ref"
case_ "Community pinned to a sha with another text" fail "differs from Upstream" \
  "mkdir -p upstream/acme/principles/$sha2/skills/principle-sample && printf 'other\n' > upstream/acme/principles/$sha2/skills/principle-sample/SKILL.md && sed -i.bak 's/sha: $sha/sha: $sha2/' $ref"
case_ "Upstream file missing at the sha" fail "cannot read Upstream" \
  "rm upstream/acme/principles/$sha/skills/principle-sample/SKILL.md"
case_ "edited file marked derived passes" ok "" \
  "sed -i.bak -e 's/Body copied/Body edited/' -e 's/status: community/status: derived/' $ref"
case_ "missing license field" fail '`license` is missing' \
  "sed -i.bak '/^license: MIT$/d' $ref"
case_ "missing Upstream" fail "no Upstream" \
  "sed -i.bak -e '/upstream: /d' -e '/path: /d' -e '/sha: /d' $ref"
case_ "missing metadata.sha" fail "metadata.sha" \
  "sed -i.bak '/  sha: /d' $ref"
case_ "short sha" fail "not a full commit sha" \
  "sed -i.bak 's/sha: $sha/sha: 1111111/' $ref"
case_ "missing Upstream license file (single form)" fail "Upstream license file is missing" \
  "rm plugins/p/skills/principles/licenses/acme-principles"
case_ "LICENSE next to the file is accepted (single form)" ok "" \
  "mv plugins/p/skills/principles/licenses/acme-principles plugins/p/skills/principles/references/LICENSE"
case_ "unknown status" fail "metadata.status is 'vendored'" \
  "sed -i.bak 's/status: community/status: vendored/' $ref"
case_ "missing license file for one of the upstreams" fail "licenses/other-ts-rules is missing" \
  "rm plugins/p/skills/stack/licenses/other-ts-rules"
case_ "upstreams entry without license" fail "is missing license" \
  "sed -i.bak '/      license: Apache-2.0/d' $stack"
case_ "both provenance forms at once" fail "use one form" \
  "perl -pi -e 's|^  status: derived\$|  status: derived\n  upstream: acme/go-skills|' $stack"

echo "check-provenance: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
