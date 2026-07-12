#!/usr/bin/env python3
"""Generate the GitHub Pages site under ``docs/`` from the Markdown chapters.

Static, self-contained HTML (plus one shared stylesheet) with the tour's
"transit diagram meets mathematical drafting" identity, a sidebar route-rail,
light/dark themes, and the interactive exposition bundled in as ``explore.html``.

Standard library only. Run from the repo root::

    python build_site.py

Then point GitHub Pages at the ``docs/`` folder (Settings -> Pages -> Deploy
from a branch -> /docs). A ``.nojekyll`` file is emitted so the raw HTML is
served as-is.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
ASSETS = DOCS / "assets"

# --------------------------------------------------------------------------- #
#  Site structure.
# --------------------------------------------------------------------------- #

STOPS = [
    ("01-depot", "The Depot"),
    ("02-unfolding-road", "The Unfolding Road"),
    ("03-engine-room", "The Engine Room"),
    ("04-golden", "The Golden Milestone"),
    ("05-scenic-overlook", "Scenic Overlook"),
    ("06-loop-road", "The Loop Road"),
    ("07-cattle-crossing", "The Cattle Crossing"),
    ("08-family-tree", "The Family Tree"),
    ("09-celebrity", "Celebrity Sightings"),
    ("10-casino", "The Casino"),
    ("11-assembly-line", "The Infinite Assembly Line"),
    ("12-tower", "The Tower"),
    ("13-hall-of-mirrors", "The Hall of Mirrors"),
    ("14-souvenir-shop", "The Souvenir Shop"),
    ("15-terminus", "Terminus"),
]

EXPRESS = [
    ("The Markov Spectrum", "The numbers after the golden ratio."),
    ("Continuants", "The polynomial inside every convergent."),
    ("Algebraic Irrationals", "Cube roots and an open problem."),
    ("Continued-Fraction Variants", "Nearest-integer and minus expansions."),
    ("The Three-Distance Theorem", "A surprise in an irrational rotation."),
    ("The Gauss-Kuzmin-Wirsing Constant", "Computed from the transfer operator."),
]

REFERENCE = [
    ("appendix-a-proofs", "Appendix A - Proofs"),
    ("appendix-b-glossary", "Appendix B - Glossary"),
    ("appendix-c-references", "Appendix C - References"),
]

FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E"
    "%3Ctext y='.9em' font-size='90'%3E%F0%9F%9A%8C%3C/text%3E%3C/svg%3E"
)

# --------------------------------------------------------------------------- #
#  Markdown -> HTML (a small converter for the features these docs use).
# --------------------------------------------------------------------------- #

_RAW_TAGS = [
    "<details>", "</details>", "<summary>", "</summary>",
    "<sub>", "</sub>", "<sup>", "</sup>", "<br>", "<br/>",
]


def rewrite_link(url: str) -> str:
    if url.startswith(("http://", "https://", "mailto:")):
        return url
    base, sep, anchor = url.partition("#")
    base = base.replace("../site/index.html", "explore.html")
    base = base.replace("site/index.html", "explore.html")
    if base.endswith(".md"):
        base = base[:-3] + ".html"
    return base + sep + anchor


def inline(text: str) -> str:
    """Inline Markdown: code, links, bold, italic; whitelisted raw tags survive."""
    # 1. protect inline code spans
    codes: list[str] = []

    def stash_code(m: re.Match) -> str:
        codes.append(html.escape(m.group(1)))
        return f"\x00C{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash_code, text)

    # 2. protect links [text](url)
    links: list[tuple[str, str]] = []

    def stash_link(m: re.Match) -> str:
        links.append((m.group(1), rewrite_link(m.group(2))))
        return f"\x00L{len(links) - 1}\x00"

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", stash_link, text)

    # 3. protect whitelisted raw HTML tags
    raws: list[str] = []
    for tag in _RAW_TAGS:
        while tag in text:
            raws.append(tag)
            text = text.replace(tag, f"\x00R{len(raws) - 1}\x00", 1)

    # 4. escape everything else
    text = html.escape(text)

    # 5. bold / italic
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)

    # 6. restore raw tags, links, code
    for i, tag in enumerate(raws):
        text = text.replace(f"\x00R{i}\x00", tag)
    for i, (label, url) in enumerate(links):
        text = text.replace(f"\x00L{i}\x00", f'<a href="{html.escape(url)}">{inline(label)}</a>')
    for i, code in enumerate(codes):
        text = text.replace(f"\x00C{i}\x00", f"<code>{code}</code>")
    return text


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", text).lower())
    return s.strip("-")


def _is_nav_strip(line: str) -> bool:
    return " · " in line and "](" in line and ("←" in line or "→" in line or "Route map" in line)


def md_to_html(text: str) -> str:
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # fenced code block
        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1  # closing fence
            cls = f' class="lang-{lang}"' if lang else ""
            out.append(f"<pre><code{cls}>{html.escape(chr(10).join(buf))}</code></pre>")
            continue

        # table
        if stripped.startswith("|"):
            table = []
            while i < n and lines[i].strip().startswith("|"):
                table.append(lines[i].strip())
                i += 1
            out.append(_render_table(table))
            continue

        # horizontal rule
        if stripped in ("---", "***", "___"):
            out.append("<hr>")
            i += 1
            continue

        # heading
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            body = inline(m.group(2))
            out.append(f'<h{level} id="{_slug(m.group(2))}">{body}</h{level}>')
            i += 1
            continue

        # blockquote
        if stripped.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].strip())
                i += 1
            out.append(f"<blockquote>{inline(' '.join(buf))}</blockquote>")
            continue

        # list (ordered or unordered), items may carry indented raw-HTML continuations
        if re.match(r"^(\d+\.|[-*])\s+", stripped):
            ordered = bool(re.match(r"^\d+\.", stripped))
            items: list[str] = []
            while i < n:
                cur = lines[i]
                mm = re.match(r"^(\d+\.|[-*])\s+(.*)$", cur.strip())
                if mm:
                    items.append(mm.group(2))
                    i += 1
                elif cur.startswith(("  ", "\t")) and cur.strip():
                    items[-1] += " " + cur.strip()  # continuation of previous item
                    i += 1
                else:
                    break
            tag = "ol" if ordered else "ul"
            body = "".join(f"<li>{inline(it)}</li>" for it in items)
            out.append(f"<{tag}>{body}</{tag}>")
            continue

        # raw HTML passthrough (a line that is only markup)
        if stripped.startswith("<") and not re.search(r"[A-Za-z]{2,}\s", stripped[:3]):
            out.append(line)
            i += 1
            continue

        # paragraph (gather consecutive plain lines)
        buf = [stripped]
        i += 1
        while i < n and lines[i].strip() and not _para_breaks(lines[i].strip()):
            buf.append(lines[i].strip())
            i += 1
        joined = " ".join(buf)
        cls = ' class="chapter-nav"' if _is_nav_strip(joined) else ""
        out.append(f"<p{cls}>{inline(joined)}</p>")
    return "\n".join(out)


def _para_breaks(stripped: str) -> bool:
    return (
        stripped.startswith(("#", ">", "|", "```", "---", "- ", "* "))
        or bool(re.match(r"^\d+\.\s", stripped))
        or stripped.startswith("<")
    )


def _render_table(rows: list[str]) -> str:
    def cells(r: str) -> list[str]:
        return [c.strip() for c in r.strip().strip("|").split("|")]

    header = cells(rows[0])
    aligns = []
    for c in cells(rows[1]):
        if c.startswith(":") and c.endswith(":"):
            aligns.append("center")
        elif c.endswith(":"):
            aligns.append("right")
        else:
            aligns.append("left")
    body = rows[2:]
    thead = "".join(
        f'<th style="text-align:{aligns[j] if j < len(aligns) else "left"}">{inline(h)}</th>'
        for j, h in enumerate(header)
    )
    trs = []
    for r in body:
        cs = cells(r)
        tds = "".join(
            f'<td style="text-align:{aligns[j] if j < len(aligns) else "left"}">{inline(c)}</td>'
            for j, c in enumerate(cs)
        )
        trs.append(f"<tr>{tds}</tr>")
    return f'<div class="tablewrap"><table><thead><tr>{thead}</tr></thead><tbody>{"".join(trs)}</tbody></table></div>'


# --------------------------------------------------------------------------- #
#  Page shell + navigation.
# --------------------------------------------------------------------------- #

def nav_html(active: str) -> str:
    def item(href: str, label: str, slug: str) -> str:
        cls = ' class="on"' if slug == active else ""
        return f'<a{cls} href="{href}">{html.escape(label)}</a>'

    parts = ['<a class="nav-home' + (' on' if active == "index" else "") + '" href="index.html">Home</a>']
    parts.append('<div class="nav-group">The Tour</div>')
    for k, (slug, title) in enumerate(STOPS, start=1):
        parts.append(item(f"{slug}.html", f"{k} · {title}", slug))
    parts.append('<div class="nav-group">The Express Line</div>')
    parts.append(item("appendix-d-frontier.html", "Fringe Avenues", "appendix-d-frontier"))
    parts.append('<div class="nav-group">Synthesis</div>')
    parts.append(item("appendix-e-web-of-ideas.html", "The Web of Ideas", "appendix-e-web-of-ideas"))
    parts.append('<div class="nav-group">Cross-Domain</div>')
    parts.append(item("appendix-f-cross-domain.html", "The Same Recurrence", "appendix-f-cross-domain"))
    parts.append('<div class="nav-group">Reference</div>')
    for slug, title in REFERENCE:
        parts.append(item(f"{slug}.html", title, slug))
    parts.append('<div class="nav-group">Interactive</div>')
    parts.append(item("explore.html", "Live Exposition ↗", "explore"))
    return "\n".join(parts)


def shell(title: str, active: str, content: str) -> str:
    nav = nav_html(active)
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="auto">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="icon" href="{FAVICON}">
<link rel="stylesheet" href="assets/rct-docs.css">
<script>
(function(){{try{{var t=localStorage.getItem('rct-theme')||'auto';document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();
</script>
</head>
<body>
<header class="topbar">
  <button class="menu-btn" aria-label="Toggle navigation" onclick="document.body.classList.toggle('nav-open')">&#9776;</button>
  <a class="wordmark" href="index.html">Recursive Continuance <b>Tour&nbsp;Bus</b></a>
  <button class="theme-toggle" id="theme-toggle" aria-label="Cycle color theme">Theme: Auto</button>
</header>
<div class="layout">
  <nav class="sidebar" aria-label="Route">{nav}</nav>
  <main class="content">{content}</main>
</div>
<footer class="site-footer">
  <span>Recursive Continuance Tour Bus &middot; a guided tour of recursion &amp; continued fractions</span>
  <span>Built from the <code>tourbus</code> engine &middot; <code>python -m tourbus</code></span>
</footer>
<script src="assets/rct-docs.js"></script>
</body>
</html>
"""


# --------------------------------------------------------------------------- #
#  Landing page.
# --------------------------------------------------------------------------- #

def landing() -> str:
    tour_cards = "\n".join(
        f'<a class="card" href="{slug}.html"><span class="card-num">{k}</span>'
        f'<span class="card-title">{html.escape(title)}</span></a>'
        for k, (slug, title) in enumerate(STOPS, start=1)
    )
    express_cards = "\n".join(
        f'<a class="card express" href="appendix-d-frontier.html#e{k}">'
        f'<span class="card-num">E{k}</span>'
        f'<span class="card-title">{html.escape(title)}</span>'
        f'<span class="card-note">{html.escape(note)}</span></a>'
        for k, (title, note) in enumerate(EXPRESS, start=1)
    )
    return f"""
<section class="hero">
  <div class="eyebrow">Line R &middot; Recursion &amp; Continued Fractions</div>
  <h1>Recursive Continuance Tour Bus</h1>
  <p class="tagline">A guided ride through the numbers that describe themselves &mdash;
  from Euclid's leftovers to Gosper's stream arithmetic, the Markov spectrum, and a
  constant nobody can write in closed form.</p>
  <div class="cta-row">
    <a class="cta primary" href="explore.html">Open the interactive exposition &nbsp;&#8599;</a>
    <a class="cta" href="01-depot.html">Start the tour &nbsp;&#8594;</a>
  </div>
  <div class="route-strip">&#9679;&#9472;&#9472;&#9679;&#9472;&#9472;&#9679;&#9472;&#9472;&#9679;&#9472;&#9472;&#9679;&#9472;&#9472;&#9679;&#9472;&#9472;&#9679;&#9472;&#9472;&#9679;&#9472;&#9472;&#9679;&#9472;&#9472;&#9679;&#9472;&#9472;&#9679;&#9472;&#9472;&#9679;&#9472;&#9472;&#9679;&#9472;&#9472;&#9679; &nbsp; 15 stops, no transfers</div>
</section>

<section>
  <h2>The Tour</h2>
  <p>Fifteen numbered stops, each with a chapter here, a live section in the
  interactive exposition, and a command-line demonstration you can run with
  <code>python -m tourbus stop N</code>.</p>
  <div class="card-grid">{tour_cards}</div>
</section>

<section>
  <h2>The Express Line</h2>
  <p>Six deeper, stranger stops past the terminus &mdash; each still computed
  exactly (or rigorously) on the same engine. See
  <a href="appendix-d-frontier.html">the Fringe Avenues</a>.</p>
  <div class="card-grid">{express_cards}</div>
</section>

<section>
  <h2>The Web of Ideas</h2>
  <p>Recursion, continued fractions, π, and physics turn out to be one gesture &mdash;
  <em>the infinite defined by finite self-application</em> &mdash; seen from four
  directions. Fixed points and the Y combinator; the Gauss map as renormalization;
  the golden ratio as the most stable orbit in KAM theory; mode-locking and the
  devil's staircase; the Hofstadter butterfly; and two elastic blocks that collide
  exactly <b>π</b> times.</p>
  <div class="cta-row">
    <a class="cta primary" href="appendix-e-web-of-ideas.html">Read the synthesis &nbsp;&#8594;</a>
    <a class="cta" href="appendix-d-frontier.html">The Express Line &nbsp;&#8594;</a>
  </div>
</section>

<section>
  <h2>The Cross-Domain Line</h2>
  <p>One three-term recurrence &mdash; the continuant behind every
  continued-fraction convergent &mdash; turns out to be the energy levels of a
  molecule, the Hofstadter butterfly of an electron in a magnetic field, the
  impedance of a circuit, the stability of a control loop, and the best rational
  summary of a divergent series; the golden ratio, meanwhile, quietly optimizes
  sunflowers and quasicrystals. Every claim is computed live on the same engine
  with <code>python -m tourbus crossdomain</code>.</p>
  <div class="cta-row">
    <a class="cta primary" href="appendix-f-cross-domain.html">The Cross-Domain Line &nbsp;&#8594;</a>
  </div>
</section>

<section>
  <h2>Reference &amp; running it</h2>
  <ul class="ref-list">
    <li><a href="appendix-a-proofs.html">Appendix A &mdash; Proofs</a></li>
    <li><a href="appendix-b-glossary.html">Appendix B &mdash; Glossary</a></li>
    <li><a href="appendix-c-references.html">Appendix C &mdash; References</a></li>
  </ul>
  <p>The whole tour is powered by <code>tourbus</code>, a standard-library-only
  Python package. Ride it in your terminal:</p>
  <pre><code>python -m tourbus            # the interactive tour
python -m tourbus --all      # the whole tour as a transcript
python -m tourbus frontier   # the Express Line
python -m tourbus demo gkw   # the Gauss-Kuzmin-Wirsing constant, from scratch</code></pre>
</section>
"""


# --------------------------------------------------------------------------- #
#  Build.
# --------------------------------------------------------------------------- #

def build() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    (DOCS / ".nojekyll").write_text("")
    (ASSETS / "rct-docs.css").write_text(CSS)
    (ASSETS / "rct-docs.js").write_text(JS)

    # landing
    (DOCS / "index.html").write_text(shell("Recursive Continuance Tour Bus", "index", landing()))

    # chapters + express + reference
    pages = [(slug, title) for slug, title in STOPS]
    pages.append(("appendix-d-frontier", "The Express Line"))
    pages.append(("appendix-e-web-of-ideas", "The Web of Ideas"))
    pages.append(("appendix-f-cross-domain", "The Same Recurrence Everywhere"))
    pages += REFERENCE
    for slug, title in pages:
        src = DOCS / f"{slug}.md"
        if not src.exists():
            print(f"  (skip missing {src.name})")
            continue
        content = md_to_html(src.read_text())
        (DOCS / f"{slug}.html").write_text(shell(f"{title} - Tour Bus", slug, content))
        print(f"  wrote {slug}.html")

    # interactive exposition -> standalone doc
    expo = (ROOT / "site" / "index.html").read_text()
    standalone = _wrap_exposition(expo)
    (DOCS / "explore.html").write_text(standalone)
    print("  wrote explore.html (interactive exposition)")


def _wrap_exposition(fragment: str) -> str:
    """Wrap the content-only exposition in a full HTML document for Pages."""
    # The fragment starts with <title>...; give it a real head/body.
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<link rel=\"icon\" href=\"{FAVICON}\">\n"
        "<style>body{margin:0}</style>\n"
        "</head>\n<body>\n"
        + fragment
        + "\n</body>\n</html>\n"
    )


# --------------------------------------------------------------------------- #
#  Assets.
# --------------------------------------------------------------------------- #

CSS = """/* Recursive Continuance Tour Bus - GitHub Pages docs */
:root{
  --page:#eceef1; --surface:#fafbfc; --ink:#12161c; --ink-2:#4a525c;
  --muted:#8b95a1; --grid:#dbe0e6; --border:rgba(18,22,28,.12); --brass:#b5751a;
  --s1:#2a78d6; --s2:#1baf7a; --s3:#c8860f; --s5:#4a3aa7; --s6:#d1483f;
  --font-sign:ui-sans-serif,"Helvetica Neue",Helvetica,Arial,sans-serif;
  --font-read:"Iowan Old Style","Charter",Georgia,"Times New Roman",serif;
  --font-data:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:dark){:root{
  --page:#0b0e13; --surface:#12171f; --ink:#eef2f7; --ink-2:#aeb7c2;
  --muted:#6b7480; --grid:#1c232d; --border:rgba(238,242,247,.12); --brass:#e0a63e;
  --s1:#4b93e6; --s2:#22b183; --s3:#e0a63e; --s5:#9085e9; --s6:#e5675c;
}}
:root[data-theme="light"]{
  --page:#eceef1; --surface:#fafbfc; --ink:#12161c; --ink-2:#4a525c;
  --muted:#8b95a1; --grid:#dbe0e6; --border:rgba(18,22,28,.12); --brass:#b5751a;
  --s1:#2a78d6; --s2:#1baf7a; --s3:#c8860f; --s5:#4a3aa7; --s6:#d1483f;
}
:root[data-theme="dark"]{
  --page:#0b0e13; --surface:#12171f; --ink:#eef2f7; --ink-2:#aeb7c2;
  --muted:#6b7480; --grid:#1c232d; --border:rgba(238,242,247,.12); --brass:#e0a63e;
  --s1:#4b93e6; --s2:#22b183; --s3:#e0a63e; --s5:#9085e9; --s6:#e5675c;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--page);color:var(--ink);font-family:var(--font-read);
  font-size:17px;line-height:1.65;-webkit-text-size-adjust:100%}
:focus-visible{outline:2px solid var(--brass);outline-offset:2px;border-radius:2px}
a{color:var(--brass);text-decoration:none}
a:hover{text-decoration:underline}
code{font-family:var(--font-data);font-size:.86em;background:color-mix(in srgb,var(--brass) 10%,transparent);
  padding:.08em .32em;border-radius:3px;font-variant-numeric:tabular-nums}
pre{background:var(--surface);border:1px solid var(--border);border-radius:5px;
  padding:.9rem 1rem;overflow-x:auto}
pre code{background:none;padding:0;font-size:.82rem;line-height:1.55}

/* topbar */
.topbar{position:sticky;top:0;z-index:30;display:flex;align-items:center;gap:.7rem;
  padding:.5rem clamp(.8rem,3vw,1.4rem);background:color-mix(in srgb,var(--page) 90%,transparent);
  backdrop-filter:blur(8px);border-bottom:1px solid var(--border)}
.wordmark{font-family:var(--font-sign);font-weight:800;font-size:.8rem;text-transform:uppercase;
  letter-spacing:.05em;color:var(--ink);margin-right:auto}
.wordmark b{color:var(--brass)}
.theme-toggle,.menu-btn{font-family:var(--font-data);font-size:.7rem;text-transform:uppercase;
  letter-spacing:.05em;background:var(--surface);color:var(--ink);border:1px solid var(--border);
  padding:.4rem .55rem;border-radius:4px;cursor:pointer;line-height:1}
.theme-toggle:hover,.menu-btn:hover{border-color:var(--brass);color:var(--brass)}
.menu-btn{display:none;font-size:1rem}

/* layout */
.layout{display:grid;grid-template-columns:270px minmax(0,1fr);max-width:1240px;margin:0 auto;
  gap:0;align-items:start}
.sidebar{position:sticky;top:52px;align-self:start;max-height:calc(100vh - 52px);overflow-y:auto;
  padding:1.2rem .8rem 2rem;border-right:1px solid var(--border);font-family:var(--font-sign);
  font-size:.86rem;display:flex;flex-direction:column;gap:.08rem}
.sidebar a{display:block;padding:.28rem .55rem;border-radius:4px;color:var(--ink-2);
  border-left:2px solid transparent}
.sidebar a:hover{background:color-mix(in srgb,var(--brass) 8%,transparent);text-decoration:none;color:var(--ink)}
.sidebar a.on{color:var(--brass);border-left-color:var(--brass);
  background:color-mix(in srgb,var(--brass) 10%,transparent);font-weight:600}
.sidebar a.nav-home{font-weight:700;color:var(--ink);margin-bottom:.3rem}
.nav-group{font-family:var(--font-data);font-size:.64rem;text-transform:uppercase;letter-spacing:.12em;
  color:var(--muted);margin:.9rem 0 .25rem .55rem}

/* content */
.content{padding:1.6rem clamp(1rem,4vw,3rem) 4rem;min-width:0;max-width:76ch}
.content h1{font-family:var(--font-sign);font-weight:800;font-size:clamp(1.8rem,4vw,2.6rem);
  line-height:1.08;letter-spacing:-.02em;text-wrap:balance;margin:.2rem 0 1rem}
.content h2{font-family:var(--font-sign);font-weight:800;font-size:1.5rem;margin:2.2rem 0 .8rem;
  padding-top:1.2rem;border-top:1px solid var(--border);text-wrap:balance}
.content h3{font-family:var(--font-sign);font-weight:700;font-size:1.12rem;margin:1.6rem 0 .5rem}
.content p{margin:0 0 1rem}
.content blockquote{margin:1rem 0;padding:.4rem 0 .4rem 1.1rem;border-left:3px solid var(--brass);
  color:var(--ink-2);font-style:italic}
.content ul,.content ol{margin:0 0 1rem;padding-left:1.4rem}
.content li{margin:.35rem 0}
.content hr{border:none;border-top:1px solid var(--border);margin:2rem 0}
.content details{margin:.4rem 0 .4rem;padding:.3rem .7rem;background:var(--surface);
  border:1px solid var(--border);border-radius:4px}
.content summary{cursor:pointer;font-family:var(--font-sign);font-size:.85rem;color:var(--brass)}
.chapter-nav{font-family:var(--font-data);font-size:.78rem;color:var(--muted);
  padding:.5rem 0;border-bottom:1px solid var(--border);margin-bottom:1.4rem}
.chapter-nav:last-of-type{border-bottom:none;border-top:1px solid var(--border);margin-top:2rem}

/* tables */
.tablewrap{overflow-x:auto;margin:1rem 0;border:1px solid var(--border);border-radius:5px}
table{border-collapse:collapse;width:100%;font-family:var(--font-data);font-size:.8rem;
  font-variant-numeric:tabular-nums}
th,td{padding:.4rem .6rem;border-bottom:1px solid var(--border);white-space:nowrap}
th{color:var(--ink-2);text-transform:uppercase;letter-spacing:.04em;font-size:.68rem;
  background:var(--surface);position:sticky;top:0}

/* hero + cards (landing) */
.hero{padding:1.5rem 0 2rem;border-bottom:1px solid var(--border);margin-bottom:1.5rem;
  background:linear-gradient(var(--grid) 1px,transparent 1px) 0 0/100% 28px,
  linear-gradient(90deg,var(--grid) 1px,transparent 1px) 0 0/28px 100%;
  border-radius:6px;padding-left:1.2rem;padding-right:1.2rem}
.eyebrow{font-family:var(--font-data);text-transform:uppercase;letter-spacing:.1em;font-size:.7rem;
  color:var(--brass);font-weight:600}
.hero h1{font-family:var(--font-sign);font-weight:800;font-size:clamp(2rem,6vw,3.4rem);
  line-height:1.02;letter-spacing:-.02em;margin:.4rem 0}
.tagline{font-family:var(--font-sign);font-weight:500;color:var(--ink-2);max-width:56ch;
  font-size:clamp(1rem,2.2vw,1.15rem)}
.cta-row{display:flex;flex-wrap:wrap;gap:.7rem;margin:1.4rem 0 1rem}
.cta{font-family:var(--font-sign);font-weight:600;font-size:.9rem;padding:.6rem 1rem;
  border:1px solid var(--border);border-radius:5px;color:var(--ink);background:var(--surface)}
.cta:hover{border-color:var(--brass);color:var(--brass);text-decoration:none}
.cta.primary{background:var(--brass);color:#fff;border-color:var(--brass)}
.cta.primary:hover{filter:brightness(1.07);color:#fff}
.route-strip{font-family:var(--font-data);font-size:.72rem;color:var(--muted);letter-spacing:.02em;
  overflow-x:auto;white-space:nowrap;padding-top:.6rem}
.card-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:.7rem;margin:1rem 0 1.5rem}
.card{display:flex;flex-direction:column;gap:.15rem;padding:.7rem .85rem;border:1px solid var(--border);
  border-radius:5px;background:var(--surface);color:var(--ink)}
.card:hover{border-color:var(--brass);text-decoration:none;transform:translateY(-1px)}
.card-num{font-family:var(--font-data);font-size:.7rem;font-weight:700;color:var(--brass)}
.card-title{font-family:var(--font-sign);font-weight:600;font-size:.92rem}
.card-note{font-size:.8rem;color:var(--ink-2)}
.ref-list{list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:.5rem 1.4rem}
.content section{margin-bottom:1rem}

/* footer */
.site-footer{max-width:1240px;margin:0 auto;padding:1.4rem clamp(1rem,4vw,3rem);
  border-top:1px solid var(--border);display:flex;flex-wrap:wrap;gap:.5rem 1.5rem;
  justify-content:space-between;font-size:.78rem;color:var(--muted);font-family:var(--font-sign)}

@media (max-width:860px){
  .layout{grid-template-columns:1fr}
  .menu-btn{display:inline-block}
  .sidebar{position:fixed;top:49px;left:0;bottom:0;width:280px;background:var(--page);z-index:25;
    transform:translateX(-105%);transition:transform .2s;border-right:1px solid var(--border)}
  body.nav-open .sidebar{transform:none}
  .content{max-width:none}
}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}.card:hover{transform:none}.sidebar{transition:none}}
"""

JS = """(function(){
  var order=['auto','light','dark'];
  var labels={auto:'Theme: Auto',light:'Theme: Light',dark:'Theme: Dark'};
  var btn=document.getElementById('theme-toggle');
  function cur(){try{return localStorage.getItem('rct-theme')||'auto';}catch(e){return 'auto';}}
  function apply(m){document.documentElement.setAttribute('data-theme',m);if(btn)btn.textContent=labels[m];}
  apply(cur());
  if(btn)btn.addEventListener('click',function(){
    var m=order[(order.indexOf(cur())+1)%3];
    try{localStorage.setItem('rct-theme',m);}catch(e){}
    apply(m);
  });
  // close mobile nav after following a link
  document.querySelectorAll('.sidebar a').forEach(function(a){
    a.addEventListener('click',function(){document.body.classList.remove('nav-open');});
  });
})();
"""


if __name__ == "__main__":
    build()
    print("Site built under docs/. Enable GitHub Pages -> Deploy from branch -> /docs.")
