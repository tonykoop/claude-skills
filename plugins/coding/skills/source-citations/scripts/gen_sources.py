#!/usr/bin/env python3
"""Generate a per-repo SOURCES.md from a curated key list — and validate it.

Two commands:

  gen <repo-dir>      Read <repo-dir>/.citations.yaml (the curated key list YOU
                      write) and emit <repo-dir>/SOURCES.md. Each cited key is
                      looked up in registry.yaml; the description, URL, and a
                      short "why this source" note YOU wrote are rendered.

  check <repo-dir>    Verify every key in .citations.yaml exists in the registry
                      and that no "why" note is blank. Exits 1 on any problem.
                      This is the integrity gate: it cannot invent citations,
                      only confirm the ones you chose resolve to real entries.

The .citations.yaml the maker writes looks like:

    instrument: Transverse Flute
    repo: transverse-flute
    cites:
      - key: demakein
        why: Generated the bore profile and tone-hole positions for this flute.
      - key: nederveen-acoustical
        why: Source for the tone-hole end-correction physics used in the model.
      - key: chiff-fipple
        why: Cross-checked embouchure-hole undercut against builder reports.

Note the design: `why` is REQUIRED and is the maker's own sentence. A citation
without a real reason is the thing that makes a "research" repo look fake, so
the tool refuses to ship one.
"""
import sys
import re
import argparse
from pathlib import Path

REGISTRY = None


def load_registry(path: Path):
    """Tiny YAML reader for the registry's known flat structure (no deps)."""
    entries = {}
    cur = None
    list_field = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if re.match(r"^\s*-\s*key:", line):
            if cur:
                entries[cur["key"]] = cur
            cur = {}
            list_field = None
            line = re.sub(r"^\s*-\s*", "", line)
        if cur is None:
            continue
        m = re.match(r"^\s*([a-z_]+):\s*(.*)$", line)
        if m:
            field, val = m.group(1), m.group(2)
            val = _scalar(val)
            cur[field] = val
    if cur:
        entries[cur["key"]] = cur
    return entries


def _scalar(v: str):
    v = _strip_inline_comment(v.strip())
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        if not inner:
            return []
        return [_unquote(x.strip()) for x in inner.split(",")]
    return _unquote(v)


def _strip_inline_comment(v: str) -> str:
    # Drop a YAML inline comment ( ` #...` ) from an unquoted scalar. A `#`
    # only starts a comment when preceded by whitespace; mid-token `#` (e.g.
    # in a URL fragment) stays. Quoted scalars pass through untouched.
    v = v.strip()
    if v.startswith('"') or v.startswith("'"):
        return v
    i = v.find(" #")
    return v[:i].rstrip() if i != -1 else v


def _unquote(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
        return v[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return v


def load_citations(path: Path):
    """Read the maker's curated .citations.yaml. Deliberately small/forgiving."""
    data = {"cites": []}
    cur = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if re.match(r"^\s*-\s*key:", line):
            if cur:
                data["cites"].append(cur)
            cur = {"key": _unquote(re.sub(r"^\s*-\s*key:\s*", "", line))}
            continue
        m = re.match(r"^\s*(instrument|repo):\s*(.*)$", line)
        if m and cur is None:
            data[m.group(1)] = _unquote(m.group(2))
            continue
        m = re.match(r"^\s*why:\s*(.*)$", line)
        if m and cur is not None:
            cur["why"] = _unquote(m.group(1))
    if cur:
        data["cites"].append(cur)
    return data


def cmd_check(repo: Path, registry):
    cit_path = repo / ".citations.yaml"
    if not cit_path.exists():
        print(f"FAIL: {cit_path} not found"); return 1
    data = load_citations(cit_path)
    problems = []
    if not data["cites"]:
        problems.append("no cites listed")
    for c in data["cites"]:
        if c["key"] not in registry:
            problems.append(f"unknown key: {c['key']} (not in registry)")
        if not c.get("why", "").strip():
            problems.append(f"key '{c['key']}' has no 'why' note (required)")
    if problems:
        print(f"FAIL ({repo.name}):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"OK: {repo.name} — {len(data['cites'])} citations, all resolve, all have rationale")
    return 0


def cmd_gen(repo: Path, registry):
    if cmd_check(repo, registry) != 0:
        print("Refusing to generate SOURCES.md until check passes.")
        return 1
    data = load_citations(repo / ".citations.yaml")
    name = data.get("instrument", repo.name)
    lines = [f"# Sources & References — {name}", "",
             "The design and build decisions in this repository draw on the "
             "sources below. Each entry notes specifically how it informed "
             "this instrument. Full catalog: the Tony Koop instrument-design "
             "source library.", ""]
    # group by bucket for readability
    by_bucket = {}
    for c in data["cites"]:
        e = registry[c["key"]]
        by_bucket.setdefault(e["bucket"], []).append((c, e))
    for bucket in sorted(by_bucket):
        lines.append(f"## {bucket}")
        lines.append("")
        for c, e in by_bucket[bucket]:
            lic = f" · _{e['license']}_" if e.get("license") else ""
            lines.append(f"- **[{e['title']}]({e['url']})**{lic}  ")
            lines.append(f"  {c['why']}")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"_{len(data['cites'])} sources cited. "
                 "Generated from `.citations.yaml` against the keyed registry; "
                 "edit the rationale there, not here._")
    out = repo / "SOURCES.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out} ({len(data['cites'])} sources)")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["gen", "check"])
    ap.add_argument("repo", type=Path)
    ap.add_argument("--registry", type=Path, default=Path("registry.yaml"))
    args = ap.parse_args()
    registry = load_registry(args.registry)
    rc = (cmd_gen if args.command == "gen" else cmd_check)(args.repo, registry)
    sys.exit(rc)


if __name__ == "__main__":
    main()
