"""Rewrite the block between the recent markers in README.md with the
most recently pushed public repos. Needs the gh CLI and GH_TOKEN."""
import json
import os
import re
import subprocess

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


def line(r):
    bits = [f"[**{r['name']}**]({r['html_url']})"]
    if r["description"]:
        desc = re.split(r"(?<=[a-z0-9)])\. ", r["description"].strip())[0]
        bits.append(desc if len(desc) <= 100 else desc[:97].rstrip() + "...")
    meta = " · ".join(x for x in (r["language"], r["pushed_at"][:10]) if x)
    return f"- {' — '.join(bits)}  \n  <sub>{meta}</sub>"


def main():
    block = "\n".join(line(r) for _, r in zip(range(LIMIT), repos()))
    text = open("README.md", encoding="utf-8").read()
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    new = pattern.sub(lambda _: f"{START}\n{block}\n{END}", text)
    if new != text:
        open("README.md", "w", encoding="utf-8", newline="\n").write(new)


if __name__ == "__main__":
    main()
