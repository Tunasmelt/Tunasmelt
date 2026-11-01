"""Generate the profile's theme-adaptive SVG assets and README.md.

Run: python scripts/build_assets.py
Edit DATA below, rerun, commit. The recent-repos block in README.md is
preserved; the telemetry SVG comes from build_telemetry.py (needs the API).
"""
import re
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
REV = "2026.11"
W = 840

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
MONO_W, SANS_W = 0.61, 0.55  # rough glyph width / font size, for layout

THEMES = {
    "dark": dict(ink="#e6edf3", muted="#7d8590", faint="#30363d", soft="#161b22",
                 accent="#3fb950", link="#58a6ff",
                 series=["#3fb950", "#58a6ff", "#bc8cff", "#d29922", "#f778ba", "#76e3ea"]),
    "light": dict(ink="#1f2328", muted="#656d76", faint="#d0d7de", soft="#f6f8fa",
                  accent="#1a7f37", link="#0969da",
                  series=["#1a7f37", "#0969da", "#8250df", "#9a6700", "#bf3989", "#1b7c83"]),
}

# ---------------------------------------------------------------- content

LINKS = [
    ("PORTFOLIO", "https://forklift22.vercel.app", "vercel"),
    ("EMAIL", "mailto:forklift027@gmail.com", "gmail"),
    ("PYPI", "https://pypi.org/project/mcp-drifter/", "pypi"),
]

HEADER = dict(
    kicker="TUNASMELT / ENGINEERING DATASHEET",
    name="Ibad Shamsi",
    role="BACKEND & AGENTIC AI ENGINEER",
    alt="Ibad Shamsi, Backend & Agentic AI Engineer",
    thesis="Agents that behave predictably, and the engineering to prove it.",
    specs=[("FOCUS", "Retrieval · Agents"), ("METHOD", "build → measure → break"),
           ("SHIPPED", "15+ public systems"), ("STATUS", "building")],
)

ABOUT = dict(
    body=("I build systems that do work on their own, then obsess over the engineering "
          "underneath them: retrieval quality, agent orchestration, evaluation, "
          "observability and failure modes."),
    quote="I care less about making an agent look intelligent than making it behave predictably.",
    specs=[("ROLE", "Backend & Agentic AI"), ("LANGUAGES", "TypeScript · Python"),
           ("BACKEND", "FastAPI · Next.js"), ("DATA", "Postgres · Supabase"),
           ("VECTORS", "pgvector · hybrid RRF"), ("ML", "PyTorch"),
           ("MOBILE", "Flutter · Expo"), ("PROTOCOLS", "MCP · SSE")],
)

# kind: featured | public | private
LAYERS = [
    ("INTERFACE", "what people touch",
     [("Struc.txt", "featured"), ("BeatLab", "public"), ("NOIR: Transit", "public"),
      ("Manifest", "public"), ("Cerebro Flutter", "public")]),
    ("AGENTS & MCP", "what acts",
     [("Drifter", "featured"), ("Reminisce", "featured"), ("TrustWright", "public"),
      ("Agent-OS", "public"), ("ForkedRap", "private")]),
    ("RETRIEVAL & INFRA", "what it knows",
     [("Docify", "featured"), ("Cerebro 2.0", "public"), ("Cachify", "public")]),
]

FEATURED = [
    dict(slug="docify", layer="RETRIEVAL", name="Docify", url="https://github.com/Tunasmelt/Docify",
         tagline="Multi-tenant SaaS for document Q&A",
         desc=("Three-tier OCR fallback, provider-partitioned RRF hybrid retrieval, "
               "SSE-streamed answers with every citation re-checked against the source."),
         tags=["Next.js 14", "FastAPI", "Supabase", "Voyage AI", "Gemini"]),
    dict(slug="reminisce", layer="AGENTS", name="Reminisce", url="https://github.com/Tunasmelt/Reminisce",
         tagline="AI context orchestration for developers",
         desc=("Define a project once; every AI call, editor session and teammate "
               "works from the same live, shareable context."),
         tags=["Next.js 14", "SaaS"]),
    dict(slug="drifter", layer="MCP", name="Drifter", url="https://github.com/Tunasmelt/Drifter-MCP",
         tagline="Regression harness for MCP tool schemas",
         desc=("A proxy on the MCP connection that records real tool-use trajectories, "
               "then mutates and replays the interface offline. Replay is experimental."),
         tags=["Python", "MCP", "PyPI"]),
    dict(slug="structxt", layer="INTERFACE", name="Struc.txt", url="https://github.com/Tunasmelt/Struc.txt",
         tagline="Structured notes from rough capture",
         desc=("Spoken or pasted notes become structured records via LLM, pinned to a "
               "draggable corkboard, with templates, auto-tags and version history."),
         tags=["LLM", "Voice", "Corkboard UI"]),
]

INDEX = [
    ("TrustWright", "https://github.com/Tunasmelt/TrustWright", "PYTHON · MCP",
     "Local stdio MCP server for evidence-scoped auth assessment; returns a recipe, never a verdict."),
    ("Cachify", "https://github.com/Tunasmelt/Cachify", "PYTHON",
     "Prompt cache gateway that diagnoses cache busts and serves safe semantic cache hits."),
    ("Cerebro 2.0", "https://github.com/Tunasmelt/Cerebro-2.0", "PYTHON · NEXT.JS",
     "Multimodal knowledge vault: hybrid RAG, live brain graph, client-side-encrypted sealed tier."),
    ("Cerebro Flutter", "https://github.com/Tunasmelt/Cerebro-Flutter", "DART",
     "Mobile client for Cerebro: Supabase auth, signed-URL uploads, SSE chat with citations."),
    ("Manifest", "https://github.com/Tunasmelt/Manifest-v2", "TYPESCRIPT",
     "Story sharing platform: Next.js 15 + Expo monorepo, TypeScript layout engine with 86 tests."),
    ("ForkedRap", None, "PRIVATE",
     "Hip-hop content pipeline: human review gate, deterministic schema-first compiler, MCP server."),
    ("Agent-OS", "https://github.com/Tunasmelt/Agent-OS", "FRAMEWORK",
     "Control layer for AI coding agents: tiered memory, gated spec → plan → TDD → review → PR."),
    ("BeatLab", "https://github.com/Tunasmelt/BeatLab", "WEB AUDIO",
     "Browser drum machine and 808 sequencer: sub-5ms scheduler drift, WAV export, share-by-URL."),
    ("NOIR: Transit", "https://github.com/Tunasmelt/Noir-Transit", "BROWSER GAME",
     "PS2-era first-person horror in the browser with fully procedural audio and two endings."),
]

SECTIONS = {
    "s01": ("01", "WHOAMI", "~/about"),
    "s02": ("02", "SYSTEM MAP", "~/fig-01"),
    "s03": ("03", "START HERE", "~/featured"),
    "s04": ("04", "INDEX", "~/other-builds"),
    "s05": ("05", "RECENTLY SHIPPED", "~/live"),
    "s06": ("06", "TELEMETRY", "~/fig-02"),
}

# ---------------------------------------------------------------- svg helpers


def attr(s):
    return escape(str(s), {'"': "&quot;"})


def text(x, y, s, size, fill, font=MONO, weight=None, anchor=None, spacing=None,
         italic=False, extra=""):
    a = [f'x="{x:g}"', f'y="{y:g}"', f'fill="{fill}"', f'font-family="{font}"',
         f'font-size="{size}"']
    if weight:
        a.append(f'font-weight="{weight}"')
    if anchor:
        a.append(f'text-anchor="{anchor}"')
    if spacing:
        a.append(f'letter-spacing="{spacing}"')
    if italic:
        a.append('font-style="italic"')
    return f'<text {" ".join(a)}>{escape(s)}{extra}</text>'


def line(x1, y1, x2, y2, stroke, extra=""):
    return f'<path d="M{x1:g} {y1:g}H{x2:g}V{y2:g}" stroke="{stroke}" fill="none"{extra}/>'


def hline(x1, x2, y, stroke):
    return f'<path d="M{x1:g} {y:g}H{x2:g}" stroke="{stroke}"/>'


def vline(x, y1, y2, stroke):
    return f'<path d="M{x:g} {y1:g}V{y2:g}" stroke="{stroke}"/>'


def width_of(s, size, factor=MONO_W, spacing=0):
    return len(s) * (size * factor + spacing)


def wrap(s, size, width, factor):
    limit = max(1, int(width / (size * factor)))
    lines, cur = [], ""
    for word in s.split():
        if cur and len(cur) + 1 + len(word) > limit:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + [cur] if cur else lines


def clip(s, size, width):
    limit = int(width / (size * MONO_W))
    return s if len(s) <= limit else s[: limit - 1].rstrip() + "…"


def pulse(cx, cy, r, fill):
    return (f'<circle cx="{cx:g}" cy="{cy:g}" r="{r}" fill="{fill}">'
            '<animate attributeName="opacity" values="1;.3;1" dur="2.4s" '
            'repeatCount="indefinite"/></circle>')


def svg(w, h, title, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:g}" height="{h:g}" '
            f'viewBox="0 0 {w:g} {h:g}" role="img" aria-label="{attr(title)}">'
            f'<title>{escape(title)}</title>{"".join(body)}</svg>\n')


def dark_overrides():
    # Every light colour is unique, so attribute selectors can swap each one
    # for its dark counterpart. CSS beats presentation attributes.
    light, dark = THEMES["light"], THEMES["dark"]
    pairs = {}
    for key, value in light.items():
        if isinstance(value, list):
            pairs.update(zip(value, dark[key]))
        else:
            pairs[value] = dark[key]
    rules = "".join(f'[fill="{l}"]{{fill:{d}}}[stroke="{l}"]{{stroke:{d}}}' for l, d in pairs.items())
    return f"<style>@media (prefers-color-scheme: dark){{{rules}}}</style>"


def write(name, render):
    """Write one SVG that adapts to the embedding page's colour scheme.

    An <img> SVG follows the page's color-scheme, which GitHub sets from the
    viewer's theme, so one file serves both themes and can sit inside a link.
    """
    content = render(THEMES["light"])
    end = content.index(">") + 1
    path = ASSETS / f"{name}.svg"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content[:end] + dark_overrides() + content[end:], encoding="utf-8", newline="\n")


# ---------------------------------------------------------------- pieces


def header(t):
    h = HEADER
    b = [text(0, 16, h["kicker"], 11, t["muted"], spacing=1.5),
         text(W, 16, f"REV {REV} · PAGE 01", 11, t["muted"], anchor="end", spacing=1.5),
         hline(0, W, 30.5, t["faint"]),
         text(-3, 104, h["name"], 60, t["ink"], SANS, 700, spacing=-1.5),
         text(0, 140, h["role"], 14, t["accent"], spacing=2.5),
         text(0, 172, h["thesis"], 17, t["muted"], SANS),
         hline(0, W, 196.5, t["faint"])]
    col = W / len(h["specs"])
    for i, (k, v) in enumerate(h["specs"]):
        x = i * col + (0 if i == 0 else 18)
        if i:
            b.append(vline(i * col + 0.5, 204, 246, t["faint"]))
        b.append(text(x, 218, k, 10, t["muted"], spacing=1.5))
        if k == "STATUS":
            b.append(pulse(x + 5, 234, 4.5, t["accent"]))
            b.append(text(x + 18, 239, v, 13, t["ink"]))
        else:
            b.append(text(x, 239, v, 13, t["ink"]))
    b.append(hline(0, W, 254.5, t["faint"]))
    return svg(W, 256, h["alt"], b)


def section(t, num, label, tag):
    lx = 58
    end = lx + width_of(label, 12, spacing=3) + 14
    b = [text(0, 42, num, 30, t["ink"], SANS, 700, spacing=-1),
         text(lx, 38, label, 12, t["ink"], weight=600, spacing=3),
         hline(end, W - width_of(tag, 11) - 14, 33.5, t["faint"]),
         text(W, 38, tag, 11, t["muted"], anchor="end")]
    return svg(W, 56, f"{num} — {label.title()}", b)


def about(t):
    a = ABOUT
    lw, b, y = 470, [], 26
    for ln in wrap(a["body"], 16, lw, SANS_W):
        b.append(text(0, y, ln, 16, t["ink"], SANS))
        y += 26
    y += 12
    q_top = y - 16
    for ln in wrap(a["quote"], 15, lw - 22, SANS_W):
        b.append(text(20, y, ln, 15, t["muted"], SANS, italic=True))
        y += 24
    b.append(f'<rect x="0" y="{q_top}" width="3" height="{y - q_top - 14}" rx="1.5" fill="{t["accent"]}"/>')
    left_h = y

    rx, ry = 520, 26
    b.append(vline(495.5, 6, 26 * len(a["specs"]) + 8, t["faint"]))
    for k, v in a["specs"]:
        kx = rx + width_of(k, 11, spacing=1) + 8
        vx = W - width_of(v, 12) - 8
        b.append(text(rx, ry, k, 11, t["muted"], spacing=1))
        b.append(f'<path d="M{kx:g} {ry - 3}H{vx:g}" stroke="{t["faint"]}" stroke-dasharray="1 4"/>')
        b.append(text(W, ry, v, 12, t["ink"], anchor="end"))
        ry += 26
    return svg(W, max(left_h, ry) + 4, "About Ibad Shamsi", b)


def fig01(t):
    label_w, x0, chip_h, gap = 190, 214, 30, 10
    b = [text(0, 14, "FIG. 01 — SYSTEMS BY LAYER", 11, t["muted"], spacing=1.5),
         text(W, 14, "request flow ↓", 11, t["muted"], anchor="end")]
    y, centers = 30, []
    for name, sub, items in LAYERS:
        rows, cx = [[]], x0
        for item, kind in items:
            w = width_of(item, 12) + 42
            if rows[-1] and cx + w > W - 18:
                rows.append([])
                cx = x0
            rows[-1].append((cx, item, kind, w))
            cx += w + gap
        rows_h = len(rows) * chip_h + (len(rows) - 1) * gap
        bh = max(84, rows_h + 40)
        b.append(f'<rect x="0.5" y="{y + .5}" width="{W - 1}" height="{bh}" rx="8" '
                 f'fill="{t["soft"]}" stroke="{t["faint"]}"/>')
        b.append(text(22, y + bh / 2 - 3, name, 11, t["ink"], weight=600, spacing=2))
        b.append(text(22, y + bh / 2 + 15, sub, 11, t["muted"]))
        cy0 = y + (bh - rows_h) / 2
        for r, row in enumerate(rows):
            cy = cy0 + r * (chip_h + gap)
            for cx, item, kind, w in row:
                mid = cy + chip_h / 2
                b.append(f'<rect x="{cx:g}" y="{cy:g}" width="{w:g}" height="{chip_h}" '
                         f'rx="{chip_h / 2}" fill="none" stroke="{t["faint"]}"/>')
                if kind == "featured":
                    b.append(f'<circle cx="{cx + 16:g}" cy="{mid:g}" r="4" fill="{t["accent"]}"/>')
                else:
                    dash = ' stroke-dasharray="2 2"' if kind == "private" else ""
                    b.append(f'<circle cx="{cx + 16:g}" cy="{mid:g}" r="3.5" fill="none" '
                             f'stroke="{t["muted"]}"{dash}/>')
                b.append(text(cx + 29, mid + 4, item, 12, t["ink"]))
        centers.append(y + bh / 2)
        y += bh + 14

    # animated request bus through every layer
    top, bottom = 30, y - 14
    b.append(vline(label_w + .5, top + 1, bottom, t["faint"]))
    b.append(f'<path d="M{label_w + .5} {top + 1}V{bottom}" stroke="{t["accent"]}" '
             'stroke-width="1.5" stroke-dasharray="3 9" opacity=".9">'
             '<animate attributeName="stroke-dashoffset" from="0" to="-24" dur="1.4s" '
             'repeatCount="indefinite"/></path>')
    for c in centers:
        b.append(f'<circle cx="{label_w + .5}" cy="{c:g}" r="4" fill="{t["soft"]}" '
                 f'stroke="{t["accent"]}" stroke-width="1.5"/>')
    ly = y + 6
    legend = [("featured", "featured"), ("public", "public"), ("private", "private")]
    lx = 0
    for kind, label in legend:
        if kind == "featured":
            b.append(f'<circle cx="{lx + 4}" cy="{ly - 4}" r="4" fill="{t["accent"]}"/>')
        else:
            dash = ' stroke-dasharray="2 2"' if kind == "private" else ""
            b.append(f'<circle cx="{lx + 4}" cy="{ly - 4}" r="3.5" fill="none" '
                     f'stroke="{t["muted"]}"{dash}/>')
        b.append(text(lx + 14, ly, label, 11, t["muted"]))
        lx += width_of(label, 11) + 40
    b.append(text(W, ly, f"{sum(len(i) for _, _, i in LAYERS)} systems · {len(LAYERS)} layers",
                  11, t["muted"], anchor="end"))
    return svg(W, ly + 6, "Figure 1: systems by layer", b)


def card(t, i, p):
    cw, ch, px = 412, 236, 24
    inner = cw - 2 * px
    b = [f'<rect x="0.5" y="0.5" width="{cw - 1}" height="{ch - 1}" rx="10" '
         f'fill="{t["soft"]}" stroke="{t["faint"]}"/>',
         text(px, 34, f"{i:02d} / {p['layer']}", 11, t["muted"], spacing=1.5),
         text(cw - px, 35, "↗", 15, t["link"], anchor="end"),
         text(px - 1, 74, p["name"], 27, t["ink"], SANS, 700, spacing=-.5)]
    y = 100
    for ln in wrap(p["tagline"], 14, inner, SANS_W):
        b.append(text(px, y, ln, 14, t["ink"], SANS))
        y += 20
    y += 8
    for ln in wrap(p["desc"], 11.5, inner, MONO_W):
        b.append(text(px, y, ln, 11.5, t["muted"]))
        y += 18

    rows, cx = [[]], px
    for tag in p["tags"]:
        w = width_of(tag, 10.5) + 16
        if rows[-1] and cx + w > cw - px:
            rows.append([])
            cx = px
        rows[-1].append((cx, tag, w))
        cx += w + 6
    ty = ch - 22 - (len(rows) - 1) * 28
    for row in rows:
        for cx, tag, w in row:
            b.append(f'<rect x="{cx:g}" y="{ty - 15}" width="{w:g}" height="22" rx="4" '
                     f'fill="none" stroke="{t["faint"]}"/>')
            b.append(text(cx + 8, ty, tag, 10.5, t["muted"]))
        ty += 28
    return svg(cw, ch, f"{p['name']}: {p['tagline']}", b)


def index_row(t, lead, name, url, meta, desc):
    b = [text(0, 24, lead, 11, t["muted"]),
         text(40, 25, name, 16, t["ink"], SANS, 700),
         text(W - 26, 24, meta, 10.5, t["muted"], anchor="end", spacing=1),
         text(W, 25, "↗" if url else "◌", 14, t["link"] if url else t["muted"], anchor="end"),
         text(40, 46, clip(desc, 12, W - 40), 12, t["muted"]),
         hline(0, W, 59.5, t["faint"])]
    return svg(W, 61, f"{name}: {desc}", b)


def colophon(t):
    b = [hline(0, W, 10.5, t["faint"]),
         text(0, 34, "END OF DATASHEET", 10.5, t["muted"], spacing=2),
         text(W, 34, "reliable systems > impressive demos", 10.5, t["muted"], anchor="end"),
         text(0, 54, f"assets generated by scripts/build_assets.py · rev {REV}", 10.5,
              t["muted"], spacing=.5)]
    return svg(W, 62, "End of datasheet", b)


# ---------------------------------------------------------------- readme


def pic(name, alt, width="100%", link=None):
    img = f'<img src="assets/{name}.svg" alt="{attr(alt)}" width="{width}"/>'
    return f'<a href="{link}">{img}</a>' if link else img


def badge(label, url, logo):
    # One neutral chip for both themes: shields.io images can't adapt.
    src = f"https://img.shields.io/badge/{label}-21262d?style=flat-square&logo={logo}&logoColor=e6edf3"
    return f'<a href="{url}"><img src="{src}" alt="{label}"/></a>'


def index_slug(name):
    return "idx-" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def readme():
    path = ROOT / "README.md"
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    m = re.search(r"<!-- recent:start -->.*?<!-- recent:end -->", old, re.S)
    recent = m.group(0) if m else "<!-- recent:start -->\n<!-- recent:end -->"

    def sec(key):
        num, label, _ = SECTIONS[key]
        return pic(key, f"{num} — {label.title()}")

    cards = []
    for i in range(0, len(FEATURED), 2):
        pair = [pic("card-" + p["slug"], p["name"] + ": " + p["tagline"], "49%", p["url"])
                for p in FEATURED[i:i + 2]]
        cards.append('<p align="center">\n' + "\n".join(pair) + "\n</p>")

    rows = [pic(index_slug(name), f"{name}: {desc}", link=url) for name, url, _, desc in INDEX]

    snake = "https://raw.githubusercontent.com/Tunasmelt/Tunasmelt/output"
    parts = [
        '<div align="center">',
        "",
        pic("header", HEADER["alt"]),
        "",
        "\n".join(badge(*l) for l in LINKS),
        "",
        "</div>",
        "",
        sec("s01"), "", pic("about", ABOUT["body"]), "",
        sec("s02"), "", pic("fig-01", "Figure 1: systems by layer"), "",
        sec("s03"), "", "\n\n".join(cards), "",
        sec("s04"), "", "\n".join(rows), "",
        "<details>\n<summary><sub>DATA &amp; ML ARCHIVE</sub></summary>\n\n"
        "| Project | What it demonstrates |\n|---|---|\n"
        "| **Liver Segmentation & Tumor Analysis** | U-Net family models for CT segmentation with segmentation-based evaluation. |\n"
        "| **Cart Abandonment Analysis** | SQL + Python + Power BI analysis of 5,000 sessions and modeled recovery opportunities. |\n"
        "| **Carbon Emission Analysis** | Raw CSV → analysis → Power BI dashboard across 142 countries. |\n"
        "\n</details>",
        "",
        sec("s05"), "", "<sub>Auto-updated daily from my most recently pushed public repos.</sub>", "",
        recent, "",
        sec("s06"), "", pic("telemetry", "Figure 2: language composition and repository counts"), "",
        '<picture><source media="(prefers-color-scheme: dark)" '
        f'srcset="{snake}/github-contribution-grid-snake-dark.svg"/>'
        f'<img src="{snake}/github-contribution-grid-snake.svg" alt="Contribution graph snake" width="100%"/></picture>',
        "",
        pic("colophon", "End of datasheet"),
        "",
    ]
    path.write_text("\n".join(parts), encoding="utf-8", newline="\n")


def main():
    write("header", header)
    write("about", about)
    write("fig-01", fig01)
    write("colophon", colophon)
    for key, (num, label, tag) in SECTIONS.items():
        write(key, lambda t, a=(num, label, tag): section(t, *a))
    for i, p in enumerate(FEATURED, 1):
        write("card-" + p["slug"], lambda t, i=i, p=p: card(t, i, p))
    for n, row in enumerate(INDEX, len(FEATURED) + 1):
        write(index_slug(row[0]), lambda t, n=n, row=row: index_row(t, f"{n:02d}", *row))
    readme()


if __name__ == "__main__":
    main()
