"""Build assets/{dark,light}/telemetry.svg from live GitHub data.

Needs the gh CLI and GH_TOKEN. Run: python scripts/build_telemetry.py
"""
import datetime
import json
import os
import subprocess

from build_assets import SANS, THEMES, W, hline, svg, text, vline, width_of, write

USER = os.environ.get("PROFILE_USER", "Tunasmelt")
TOP = 6


def gh(path):
    out = subprocess.run(["gh", "api", path], check=True, capture_output=True,
                         text=True, encoding="utf-8").stdout
    return json.loads(out)


def collect():
    repos = [r for r in gh(f"users/{USER}/repos?per_page=100&type=owner")
             if not r["fork"] and r["name"].lower() != USER.lower()]
    totals = {}
    for r in repos:
        for lang, n in gh(f"repos/{r['full_name']}/languages").items():
            totals[lang] = totals.get(lang, 0) + n
    year = str(datetime.date.today().year)
    return dict(
        repos=len(repos),
        languages=totals,
        last_push=max(r["pushed_at"] for r in repos)[:10],
        new_this_year=sum(r["created_at"].startswith(year) for r in repos),
    )


def render(t, d):
    total = sum(d["languages"].values()) or 1
    ranked = sorted(d["languages"].items(), key=lambda kv: -kv[1])
    shares = [(k, v / total) for k, v in ranked[:TOP]]
    rest = 1 - sum(s for _, s in shares)
    if rest > 0.0005:
        shares.append(("Other", rest))

    stats = [(str(d["repos"]), "PUBLIC REPOS"), (str(len(d["languages"])), "LANGUAGES"),
             (str(d["new_this_year"]), f"NEW IN {datetime.date.today().year}"),
             (d["last_push"][5:].replace("-", "."), "LAST PUSH")]
    b = [text(0, 14, "FIG. 02 — LANGUAGE COMPOSITION", 11, t["muted"], spacing=1.5),
         text(W, 14, "public, non-fork repos · by bytes", 11, t["muted"], anchor="end"),
         hline(0, W, 26.5, t["faint"])]
    col = W / len(stats)
    for i, (value, label) in enumerate(stats):
        x = i * col + (0 if i == 0 else 18)
        if i:
            b.append(vline(i * col + .5, 36, 96, t["faint"]))
        b.append(text(x - 1, 74, value, 34, t["ink"], SANS, 700, spacing=-1))
        b.append(text(x, 94, label, 10, t["muted"], spacing=1.5))

    by, bh = 118, 10
    b.append(f'<clipPath id="bar"><rect x="0" y="{by}" width="{W}" height="{bh}" rx="5"/></clipPath>')
    b.append('<g clip-path="url(#bar)">')
    x = 0.0
    colors = t["series"] + [t["faint"]]
    for i, (lang, share) in enumerate(shares):
        w = W * share
        fill = t["faint"] if lang == "Other" else colors[i]
        b.append(f'<rect x="{x:.2f}" y="{by}" width="{w + .6:.2f}" height="{bh}" fill="{fill}"/>')
        x += w
    b.append("</g>")

    per_row, lx_w = 4, W / 4
    for i, (lang, share) in enumerate(shares):
        lx, ly = (i % per_row) * lx_w, 152 + (i // per_row) * 24
        fill = t["faint"] if lang == "Other" else colors[i]
        b.append(f'<rect x="{lx:g}" y="{ly - 9}" width="9" height="9" rx="2" fill="{fill}"/>')
        b.append(text(lx + 17, ly, lang, 12, t["ink"]))
        b.append(text(lx + 17 + width_of(lang, 12) + 8, ly, f"{share * 100:.1f}%", 12, t["muted"]))
    h = 152 + ((len(shares) - 1) // per_row) * 24 + 12
    return svg(W, h, "Figure 2: language composition and repository counts", b)


def main():
    data = collect()
    for theme, t in THEMES.items():
        write("telemetry", theme, render(t, data))


if __name__ == "__main__":
    main()
