"""Rebuild the recently-shipped rows: assets/recent-N.svg plus
the block between the recent markers in README.md. Needs gh and GH_TOKEN."""
import json
import os
import re
import subprocess

from build_assets import ROOT, index_row, pic, write

USER = os.environ.get("PROFILE_USER", "Tunasmelt")
LIMIT = 6
START, END = "<!-- recent:start -->", "<!-- recent:end -->"


def repos():
    out = subprocess.run(
        ["gh", "api", f"users/{USER}/repos?sort=pushed&per_page=50&type=owner"],
        check=True, capture_output=True, text=True, encoding="utf-8",
    ).stdout
    for r in json.loads(out):
        if r["fork"] or r["archived"] or r["name"].lower() == USER.lower():
            continue
        yield r


def main():
    lines = []
    for i, r in zip(range(1, LIMIT + 1), repos()):
        desc = re.split(r"(?<=[a-z0-9)])\. ", (r["description"] or "").strip())[0] or "—"
        lead = r["pushed_at"][5:10].replace("-", ".")
        meta = (r["language"] or "").upper()
        write(f"recent-{i}", lambda t: index_row(t, lead, r["name"], r["html_url"], meta, desc))
        lines.append(pic(f"recent-{i}", f"{r['name']}: {desc}", link=r["html_url"]))

    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    block = f"{START}\n" + "\n".join(lines) + f"\n{END}"
    new = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
    if new != text:
        path.write_text(new, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
