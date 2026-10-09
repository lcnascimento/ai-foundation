#!/usr/bin/env python3
"""PROTOTYPE (AI-11): grades the headless runs. Usage: analyze.py <runs-dir> <scenarios.tsv>"""
import json, re, sys, glob, os, collections

runs, scen_file = sys.argv[1], sys.argv[2]
expected = {}
for line in open(scen_file):
    sid, exp, _ = line.rstrip("\n").split("\t", 2)
    expected[sid] = exp
names = sorted({os.path.basename(p).removeprefix("principle-") for p in glob.glob(
    os.path.join(os.path.dirname(scen_file), "variants/b-skill-per-principle/skills/*"))})

def loaded_name(tool, inp):
    if tool == "Skill":
        s, a = inp.get("skill", ""), (inp.get("args") or "").strip()
        if s.endswith(":principles") or s == "principles":
            return a.removeprefix("principle-") or "?"
        m = re.search(r"principle-([a-z-]+)$", s)
        return m.group(1) if m else None
    text = json.dumps(inp)
    m = re.search(r"(?:references/|principle-)([a-z-]+?)(?:\.md|/SKILL\.md)", text)
    return m.group(1) if m and m.group(1) in names else None

def cited(text):
    t = text.lower()
    return sorted(n for n in names if n in t or n.replace("-", " ") in t)

rows = collections.defaultdict(list)
for f in sorted(glob.glob(os.path.join(runs, "*", "*.jsonl"))):
    variant = os.path.basename(os.path.dirname(f))
    sid = re.sub(r"-r\d+\.jsonl$", "", os.path.basename(f))
    ctx0, loads, first_edit, step, result, cost, turns = None, [], None, 0, "", None, None
    for line in open(f):
        try: ev = json.loads(line)
        except ValueError: continue
        if ev.get("type") == "assistant":
            msg = ev["message"]
            if ctx0 is None and msg.get("usage"):
                u = msg["usage"]
                ctx0 = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
            for c in msg.get("content", []):
                if c.get("type") != "tool_use": continue
                step += 1
                writes = c["name"] in ("Edit", "Write", "MultiEdit") or (c["name"] == "Bash" and re.search(
                    r"cat\s*>|sed -i|perl -\w*i|\.write\(|>\s*\S+\.go|\btee\b|gofmt -w", c["input"].get("command", "")))
                if writes and first_edit is None:
                    first_edit = step
                n = loaded_name(c["name"], c.get("input", {}))
                if n and n not in [l for l, _ in loads]:
                    loads.append((n, step))
        elif ev.get("type") == "result":
            result, cost, turns = ev.get("result") or "", ev.get("total_cost_usd"), ev.get("num_turns")
    exp = expected[sid]
    hit = any(n == exp for n, _ in loads)
    timely = any(n == exp and (first_edit is None or s < first_edit) for n, s in loads)
    rows[variant].append(dict(sid=sid, exp=exp, ctx0=ctx0, loads=[n for n, _ in loads], hit=hit, timely=timely,
                              cited=cited(result), cost=cost or 0, turns=turns, first_edit=first_edit))

base = [r["ctx0"] for r in rows.get("0-none", []) if r["ctx0"]]
base = min(base) if base else 0
print("| variant | expected loaded | before 1st edit | expected cited | loads/run | control loads | ctx at turn 1 (Δ vs none) | cost |")
print("|---|---|---|---|---|---|---|---|")
for v, rs in sorted(rows.items()):
    task = [r for r in rs if r["exp"] != "-"]
    ctrl = [r for r in rs if r["exp"] == "-"]
    ctx = min(r["ctx0"] for r in rs if r["ctx0"])
    print(f"| {v} | {sum(r['hit'] for r in task)}/{len(task)} | {sum(r['timely'] for r in task)}/{len(task)} | "
          f"{sum(r['exp'] in r['cited'] for r in task)}/{len(task)} | {sum(len(r['loads']) for r in task)/max(len(task),1):.1f} | "
          f"{sum(len(r['loads']) for r in ctrl)} | {ctx} ({ctx-base:+}) | ${sum(r['cost'] for r in rs):.2f} |")
print()
for v, rs in sorted(rows.items()):
    print(f"### {v}")
    for r in rs:
        print(f"- {r['sid']}: loaded={r['loads']} cited={r['cited']} first_edit_step={r['first_edit']} turns={r['turns']}")
