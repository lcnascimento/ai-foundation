#!/usr/bin/env python3
"""Provenance check for vendored and derived skill files (ADR-0001, ADR-0010).

Scans every Markdown file under plugins/*/skills/ (each SKILL.md and each
reference, e.g. a Principle under skills/principles/references/). A file whose
frontmatter has `metadata.status` must carry coherent provenance:

- `status` is `community` or `derived`, and `license` is set.
- Exactly one Upstream form:
  - single: `metadata.upstream` (GitHub `owner/repo`), `metadata.path`,
    `metadata.sha`; license file `LICENSE` next to the file, or
    `licenses/<owner>-<repo>` in the skill directory;
  - list: `metadata.upstreams`, each entry with `repo`, `sha`, `path`,
    `license`; one `licenses/<owner>-<repo>` per Upstream in the skill directory.
- `sha` is a full 40-char commit sha.
- `community` (single form only): the file equals the Upstream file at that sha
  byte for byte, once the provenance keys (`license`, `metadata`) are removed
  from the frontmatter of both.

Files without `metadata.status` (Custom skills, Custom Principles) are skipped.

Upstream files are fetched from raw.githubusercontent.com. Set
PROVENANCE_UPSTREAM_DIR to read `<dir>/<owner>/<repo>/<sha>/<path>` from disk
instead (tests, offline runs).

Usage: scripts/check-provenance.py [repo-root]   (default: this repo)
Exit 1 and one `FAIL:` line per problem when anything is off.
"""

import os
import re
import sys
import urllib.request
from pathlib import Path

import yaml

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
STATUSES = ("community", "derived")
_cache = {}


def split_frontmatter(text):
    """Return (frontmatter, body) or (None, text) when there is none."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 3)
    if end == -1:
        return None, text
    return text[4 : end + 1], text[end + 5 :]


def strip_provenance(text):
    """Drop top-level `license:` and `metadata:` (with its indented block) from the frontmatter."""
    fm, body = split_frontmatter(text)
    if fm is None:
        return text
    kept, skipping = [], False
    for line in fm.splitlines(keepends=True):
        if line.strip() and line[:1] not in (" ", "\t", "-"):  # a top-level key
            skipping = line.startswith(("license:", "metadata:"))
        if not skipping:
            kept.append(line)
    return "---\n" + "".join(kept) + "---\n" + body


def normalize_repo(repo):
    repo = str(repo).strip()
    repo = re.sub(r"^(https?://)?github\.com/", "", repo)
    repo = re.sub(r"\.git$", "", repo).strip("/")
    return repo if re.fullmatch(r"[\w.-]+/[\w.-]+", repo) else None


def fetch_upstream(repo, sha, path):
    key = (repo, sha, path)
    if key in _cache:
        return _cache[key]
    local = os.environ.get("PROVENANCE_UPSTREAM_DIR")
    if local:
        p = Path(local) / repo / sha / path
        data = p.read_bytes() if p.is_file() else None
    else:
        url = f"https://raw.githubusercontent.com/{repo}/{sha}/{path}"
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                data = r.read()
        except Exception:
            data = None
    _cache[key] = data
    return data


def skill_dir(file, plugins_dir):
    """plugins/<plugin>/skills/<skill>/..."""
    rel = file.relative_to(plugins_dir).parts
    return plugins_dir.joinpath(*rel[:3])


def check_file(file, plugins_dir, root):
    """Return (checked, errors): whether the file has metadata.status, and its problems."""
    errors = []
    rel = file.relative_to(root)
    text = file.read_text(encoding="utf-8")
    fm, _ = split_frontmatter(text)
    if fm is None:
        return False, errors
    try:
        meta = yaml.safe_load(fm) or {}
    except yaml.YAMLError as e:
        return False, [f"{rel}: frontmatter is not valid YAML ({e})"]
    md = meta.get("metadata") if isinstance(meta, dict) else None
    if not isinstance(md, dict) or "status" not in md:
        return False, errors

    def err(msg):
        errors.append(f"{rel}: {msg}")

    status = md.get("status")
    if status not in STATUSES:
        err(f"metadata.status is {status!r}, expected one of {', '.join(STATUSES)}")
    if not str(meta.get("license") or "").strip():
        err("`license` is missing")

    sdir = skill_dir(file, plugins_dir)
    single = [k for k in ("upstream", "path", "sha") if k in md]
    listed = md.get("upstreams")

    if single and listed is not None:
        err("has both metadata.upstream* and metadata.upstreams; use one form")
    elif listed is not None:
        if not isinstance(listed, list) or not listed:
            err("metadata.upstreams must be a non-empty list")
            listed = []
        if status == "community":
            err("metadata.upstreams is only for derived skills; a Community file has one Upstream")
        for i, up in enumerate(listed):
            if not isinstance(up, dict):
                err(f"metadata.upstreams[{i}] must be a mapping")
                continue
            missing = [k for k in ("repo", "sha", "path", "license") if not str(up.get(k) or "").strip()]
            if missing:
                err(f"metadata.upstreams[{i}] is missing {', '.join(missing)}")
            repo = normalize_repo(up.get("repo", ""))
            if up.get("repo") and not repo:
                err(f"metadata.upstreams[{i}].repo {up.get('repo')!r} is not a GitHub owner/repo")
            if up.get("sha") and not SHA_RE.match(str(up["sha"])):
                err(f"metadata.upstreams[{i}].sha is not a full commit sha")
            if repo:
                lic = sdir / "licenses" / repo.replace("/", "-")
                if not lic.is_file() or lic.stat().st_size == 0:
                    err(f"license file {lic.relative_to(root)} is missing or empty")
    elif single:
        missing = [k for k in ("upstream", "path", "sha") if not str(md.get(k) or "").strip()]
        if missing:
            err(f"metadata is missing {', '.join('metadata.' + k for k in missing)}")
        repo = normalize_repo(md.get("upstream", ""))
        if md.get("upstream") and not repo:
            err(f"metadata.upstream {md.get('upstream')!r} is not a GitHub owner/repo")
        sha = str(md.get("sha") or "")
        if sha and not SHA_RE.match(sha):
            err("metadata.sha is not a full commit sha")
        if repo:
            candidates = [file.parent / "LICENSE", sdir / "licenses" / repo.replace("/", "-")]
            if not any(c.is_file() and c.stat().st_size > 0 for c in candidates):
                err(
                    "Upstream license file is missing: expected "
                    + " or ".join(str(c.relative_to(root)) for c in candidates)
                )
        if status == "community" and repo and SHA_RE.match(sha) and md.get("path"):
            upstream = fetch_upstream(repo, sha, str(md["path"]))
            if upstream is None:
                err(f"cannot read Upstream {repo}@{sha}:{md['path']}")
            elif strip_provenance(text) != strip_provenance(upstream.decode("utf-8")):
                err(f"differs from Upstream {repo}@{sha}:{md['path']} (edits beyond provenance frontmatter make it `derived`)")
    else:
        err("has metadata.status but no Upstream (metadata.upstream/path/sha or metadata.upstreams)")
    return True, errors


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent).resolve()
    plugins_dir = root / "plugins"
    files = sorted(p for p in plugins_dir.glob("*/skills/**/*.md") if p.is_file())
    errors, checked = [], 0
    for f in files:
        has_status, errs = check_file(f, plugins_dir, root)
        checked += has_status
        errors += errs
    for e in errors:
        print(f"FAIL: {e}", file=sys.stderr)
    print(f"provenance: {checked} file(s) with metadata.status checked, {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
