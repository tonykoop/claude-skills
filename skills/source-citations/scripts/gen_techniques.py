#!/usr/bin/env python3
"""Manage the techniques registry: validate, generate per-repo files, build a
Quarto site. Companion to gen_sources.py; same integrity rules.

Commands:
  check  <repo-dir>     Validate <repo-dir>/.techniques.yaml: every key exists
                        in the techniques registry, every cite has a `why`, and
                        NO cited technique is status: unconfirmed. Exit 1 on fail.
  gen    <repo-dir>     Write <repo-dir>/TECHNIQUES.md from the curated key list.
  site   <out.qmd>      Render the whole confirmed registry to a Quarto .qmd with
                        videos embedded at their timestamps via {{< video ... >}}.
  audit                 List registry entries by status (confirmed/unconfirmed).

Integrity rules enforced here:
  * A repo may only cite CONFIRMED techniques. Unconfirmed seeds are pointers
    for the maker, never citations — citing one would put an unverified
    timestamp in front of a reader.
  * `start` is only emitted to the Quarto site for confirmed entries.
"""
import sys
import re
import argparse
from pathlib import Path


def _unquote(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
        return v[1:-1]
    return v


def _strip_inline_comment(v: str) -> str:
    # Strip a YAML inline comment ( ` #...` ) from an unquoted scalar. A `#`
    # only starts a comment when preceded by whitespace; mid-token `#` (e.g. in
    # a URL fragment) stays. Quoted scalars pass through untouched.
    v = v.strip()
    if v.startswith('"') or v.startswith("'"):
        return v
    i = v.find(" #")
    return v[:i].rstrip() if i != -1 else v


def _scalar(v: str):
    v = _strip_inline_comment(v.strip())
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return [_unquote(x.strip()) for x in inner.split(",")] if inner else []
    return _unquote(v)


def load_registry(path: Path):
    """Parse techniques.yaml. Handles block scalars (>-) for what_they_show."""
    entries = {}
    cur = None
    pending_block = None      # (field, indent)
    block_lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if pending_block is not None:
            field, indent = pending_block
            if raw.strip() == "" or (len(raw) - len(raw.lstrip())) > indent:
                block_lines.append(raw.strip())
                continue
            else:
                cur[field] = " ".join(x for x in block_lines if x).strip()
                pending_block, block_lines = None, []
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if re.match(r"^\s*-\s*key:", line):
            if cur:
                entries[cur["key"]] = cur
            cur = {"key": _unquote(re.sub(r"^\s*-\s*key:\s*", "", line))}
            continue
        if cur is None:
            continue
        m = re.match(r"^(\s*)([a-z_]+):\s*(.*)$", line)
        if m:
            indent, field, val = len(m.group(1)), m.group(2), m.group(3)
            if val.strip() in (">-", ">", "|", "|-"):
                pending_block = (field, indent)
                block_lines = []
            else:
                cur[field] = _scalar(val)
    if pending_block is not None and cur is not None:
        cur[pending_block[0]] = " ".join(x for x in block_lines if x).strip()
    if cur:
        entries[cur["key"]] = cur
    return entries


def load_citations(path: Path):
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
            data[m.group(1)] = _unquote(m.group(2)); continue
        m = re.match(r"^\s*why:\s*(.*)$", line)
        if m and cur is not None:
            cur["why"] = _unquote(m.group(1))
    if cur:
        data["cites"].append(cur)
    return data


def cmd_check(repo: Path, reg):
    p = repo / ".techniques.yaml"
    if not p.exists():
        print(f"FAIL: {p} not found"); return 1
    data = load_citations(p)
    problems = []
    for c in data["cites"]:
        e = reg.get(c["key"])
        if e is None:
            problems.append(f"unknown technique key: {c['key']}")
            continue
        if e.get("status") != "confirmed":
            problems.append(f"key '{c['key']}' is status:{e.get('status')} — only confirmed techniques may be cited")
        if not c.get("why", "").strip():
            problems.append(f"key '{c['key']}' has no 'why' note")
    if problems:
        print(f"FAIL ({repo.name}):")
        for p_ in problems:
            print(f"  - {p_}")
        return 1
    print(f"OK: {repo.name} — {len(data['cites'])} techniques, all confirmed, all have rationale")
    return 0


def cmd_gen(repo: Path, reg):
    if cmd_check(repo, reg) != 0:
        print("Refusing to generate TECHNIQUES.md until check passes."); return 1
    data = load_citations(repo / ".techniques.yaml")
    name = data.get("instrument", repo.name)
    out = [f"# Techniques & Demonstrations — {name}", "",
           "Builders and demonstrations that informed how this was made. "
           "Each note says how it shaped this build.", ""]
    for c in data["cites"]:
        e = reg[c["key"]]
        ts = ""
        if e.get("start"):
            mm, ss = divmod(int(e["start"]), 60)
            ts = f" @ {mm}:{ss:02d}"
        out.append(f"- **{e['technique']}** — {e['creator']} ([{e['platform']}]({e['url']}){ts})  ")
        out.append(f"  {c['why']}")
    out += ["", "---", "", f"_{len(data['cites'])} techniques cited. "
            "Edit `.techniques.yaml` and regenerate; do not hand-edit._"]
    (repo / "TECHNIQUES.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Wrote {repo/'TECHNIQUES.md'}")
    return 0


def cmd_site(out_path: Path, reg):
    confirmed = [e for e in reg.values() if e.get("status") == "confirmed"]
    pending = [e for e in reg.values() if e.get("status") != "confirmed"]
    L = ["---", "title: \"Techniques Catalog\"",
         "format:\n  html:\n    toc: true\n    embed-resources: false", "---", "",
         "Demonstrations of technique by real makers. Videos jump to the exact "
         "moment shown. The companion source bibliography covers the underlying "
         "tools and theory.", ""]
    if confirmed:
        L.append("## Confirmed demonstrations\n")
        for e in confirmed:
            L.append(f"### {e['technique']} — {e['creator']}\n")
            if e.get("what_they_show"):
                L.append(e["what_they_show"] + "\n")
            if e.get("platform") == "youtube" and e.get("start"):
                L.append(f'{{{{< video {e["url"]} start="{e["start"]}" >}}}}\n')
            else:
                L.append(f"[{e['platform']}]({e['url']})\n")
    L.append("## Unconfirmed seeds (not citable)\n")
    L.append("These are real makers/pages, but the specific technique moment is "
             "not yet verified. Watch, then promote to confirmed.\n")
    for e in pending:
        L.append(f"- **{e['creator']}** — {e['technique']} "
                 f"([{e['platform']}]({e['url']}))")
    out_path.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"Wrote {out_path} ({len(confirmed)} confirmed, {len(pending)} seeds)")
    print("Render with: quarto render", out_path)
    return 0


def cmd_audit(reg):
    for status in ("confirmed", "unconfirmed"):
        ks = [k for k, e in reg.items() if e.get("status", "unconfirmed") == status]
        print(f"{status}: {len(ks)}")
        for k in ks:
            print(f"  - {k}: {reg[k]['creator']} / {reg[k]['technique']}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["check", "gen", "site", "audit"])
    ap.add_argument("target", type=Path, nargs="?")
    ap.add_argument("--registry", type=Path, default=Path("references/techniques.yaml"))
    args = ap.parse_args()
    reg = load_registry(args.registry)
    if args.command == "audit":
        sys.exit(cmd_audit(reg))
    if args.command == "site":
        sys.exit(cmd_site(args.target or Path("techniques-catalog.qmd"), reg))
    if args.target is None:
        print("repo dir required"); sys.exit(2)
    sys.exit((cmd_check if args.command == "check" else cmd_gen)(args.target, reg))


if __name__ == "__main__":
    main()
