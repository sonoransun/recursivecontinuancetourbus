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
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
ASSETS = DOCS / "assets"

# The engine (figures) lives under src/; the mermaid renderer sits beside this
# script. Neither home is guaranteed to be on sys.path when this module is
# loaded by file path (pytest) rather than run as a script, so add both.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from build_mermaid import MermaidError, render_diagram  # noqa: E402,F401
from tourbus.figures import FIGURES  # noqa: E402

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

# Curated landing-card copy for the Express-line sections of Appendix D. The
# card count and anchors are derived from the "## E..." headings at build
# time; entries here only supply the blurbs (extras fall back to the heading).
EXPRESS = [
    ("The Markov Spectrum", "The numbers after the golden ratio."),
    ("Continuants", "The polynomial inside every convergent."),
    ("Algebraic Irrationals", "Cube roots and an open problem."),
    ("Continued-Fraction Variants", "Nearest-integer and minus expansions."),
    ("The Three-Distance Theorem", "A surprise in an irrational rotation."),
    ("The Gauss-Kuzmin-Wirsing Constant", "Computed from the transfer operator."),
    ("Colliding Blocks", "Counting π with elastic collisions."),
    ("The River", "Conway's topograph walks x² − dy² to Pell."),
    ("Ramanujan's Continued Fraction", "A q-fraction that collapses to the golden ratio."),
]

# Curated landing-card copy for the Heritage-line sections of Appendix H,
# same mechanism as EXPRESS: the card count and anchors come from the
# "## H..." headings at build time; entries here only supply the blurbs.
HERITAGE = [
    ("The Ladder of Euclid",
     "Anthyphairesis: the continued fraction, three centuries before Christ "
     "and two millennia before its name."),
    ("The Cyclic Method",
     "Fermat's challenge, solved in Sanskrit verse five hundred years early."),
    ("First Fractions in Print",
     "Bombelli, Cataldi, Brouncker: a notation, a name, and pi's first formula."),
    ("The Planetarium",
     "Huygens cuts Saturn's orbit into 206 brass teeth."),
    ("Lambert's Trial of Pi",
     "The tangent testifies, and pi is proved irrational."),
    ("The Skyscraper of Liouville",
     "A number built to be approximated: the first proven transcendental."),
    ("The Tree in the Workshop",
     "Stern's blackboard and Brocot's gears grow the same tree of fractions."),
    ("The Factoring Machine",
     "CFRAC cracks F7: convergents turned against the integers."),
    ("Item 101",
     "Gosper's memo teaches arithmetic to stream forever."),
]

# Curated landing-card copy for the Branch-line sections of Appendix I, same
# mechanism as EXPRESS/HERITAGE: card count and anchors come from the "## B..."
# headings at build time; entries here only supply the blurbs.
BRANCH = [
    ("Engel Expansions", "The ascending staircase: ceilings where the continued fraction takes floors."),
    ("Lüroth and Pierce", "The honest casino, and a rational that loops forever."),
    ("Egyptian Fractions", "The greedy scribe and the Erdős-Straus problem."),
    ("Zeckendorf and the Golden Base", "Integers written in Fibonacci, and base-φ."),
    ("Cutting Sequences", "Ostrowski numeration and Sturmian words on ticker tape."),
    ("Lochs' Theorem", "The exchange rate between digits and quotients."),
]

# The interactive exposition (explore.html) has no Markdown source, so its
# widget sections are hand-listed here to make them searchable. Each id must
# match a "<section id=...>" in site/index.html so search hits resolve.
EXPLORE_SECTIONS = [
    ("stop-1-depot", "Stop 1 - CF Expansion Machine (W1)",
     "Type a number or fraction and step Euclid's algorithm into its continued fraction; the convergents table updates live."),
    ("stop-4-golden", "Stop 4 - Golden Spiral & Irrationality Racer (W3, W4)",
     "The golden spiral at any depth and ratio, and a race of the convergent errors of phi, e, and pi."),
    ("stop-5-scenic-overlook", "Stop 5 - Calendar Designer (W9)",
     "Design a leap-year rule as a convergent of the tropical year, 0.242190 days."),
    ("stop-7-cattle-crossing", "Stop 7 - Pell Playground (W7)",
     "Enter d and watch the convergent at the period boundary light up as the fundamental solution of x^2 - d y^2 = 1."),
    ("stop-8-family-tree", "Stop 8 - Stern-Brocot Explorer (W2)",
     "Descend the mediant tree left and right to locate any fraction in lowest terms."),
    ("stop-10-casino", "Stop 10 - Gauss Map Cobweb & Khinchin Lab (W5, W6)",
     "Iterate the Gauss map T(x) = {1/x} as a cobweb, and watch the geometric mean of partial quotients approach Khinchin's constant."),
    ("stop-13-hall-of-mirrors", "Stop 13 - Fractal Lab (W8)",
     "Draw the Koch, dragon, Sierpinski, and Hilbert curves at any depth."),
    ("stop-14-souvenir-shop", "Stop 14 - Temperament Studio, Wiener Attack, Collatz (W10, W11, W12)",
     "Musical temperament tables, a small-exponent RSA break by convergents, and the Collatz orbit plotter."),
    ("stop-encore-blocks", "Encore - Colliding Blocks Count Pi (W13)",
     "A mass ratio of 100^n makes two elastic blocks collide the digits of pi times."),
    ("stop-crossdomain-butterfly", "Cross-Domain - Hofstadter Butterfly (W14)",
     "The fractal spectrum of an electron in a magnetic field, drawn from continuant Sturm sequences versus flux p/q."),
    ("stop-branch-bazaar", "Branch - The Expansion Bazaar (W15)",
     "Enter one number and see it unfolded five ways at once: continued fraction, Engel, Pierce, greedy Egyptian, and Zeckendorf, with the error of each."),
]

REFERENCE = [
    ("appendix-a-proofs", "Appendix A - Proofs"),
    ("appendix-b-glossary", "Appendix B - Glossary"),
    ("appendix-c-references", "Appendix C - References"),
    ("appendix-g-hints", "Appendix G - Hints & selected answers"),
    ("syllabus", "Syllabus - for instructors"),
]

FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E"
    "%3Ctext y='.9em' font-size='90'%3E%F0%9F%9A%8C%3C/text%3E%3C/svg%3E"
)

# Early theme bootstrap: stamp data-theme on :root before first paint so the
# saved theme applies without a flash. Shared by every page shell and the
# wrapped exposition.
THEME_BOOTSTRAP = (
    "<script>\n"
    "(function(){try{var t=localStorage.getItem('rct-theme')||'auto';"
    "document.documentElement.setAttribute('data-theme',t);}catch(e){}})();\n"
    "</script>"
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


def md_to_html(text: str, src_name: str = "?") -> str:
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
            fence_line = i + 1  # absolute 1-based line of the opening fence
            lang = stripped[3:].strip()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1  # closing fence
            if lang == "mermaid":
                out.append(render_diagram("\n".join(buf), src_name=src_name,
                                          line_no=fence_line))
                continue
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

        # block-level figure: ![caption](assets/fig-*.svg) alone on its line
        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", stripped)
        if m:
            out.append(_figure_html(m.group(1), m.group(2), src_name, i + 1))
            i += 1
            continue

        # paragraph (gather consecutive plain lines)
        buf = [stripped]
        i += 1
        while i < n and lines[i].strip() and not _para_breaks(lines[i].strip()):
            buf.append(lines[i].strip())
            i += 1
        joined = " ".join(buf)
        if "![" in joined:
            raise SystemExit(
                f"{src_name}: inline image syntax is not supported; "
                "put ![...](...) on its own line"
            )
        cls = ' class="chapter-nav"' if _is_nav_strip(joined) else ""
        out.append(f"<p{cls}>{inline(joined)}</p>")
    return "\n".join(out)


def _figure_html(
    caption: str, src: str, src_name: str, line_no: int, base: Path = DOCS
) -> str:
    """Inline a committed figure asset as a ``<figure>`` with its caption.

    Only ``assets/fig-*.svg`` paths that exist under ``base`` are accepted;
    ``build()`` writes every ``FIGURES`` entry before the page loop, so
    existence is exactly manifest membership. The SVG document is inlined
    (no ``<img>``), which lets the stylesheet re-theme it via CSS variables.
    """
    ok = src.startswith("assets/fig-") and src.endswith(".svg") and (base / src).exists()
    if not ok:
        raise SystemExit(f"{src_name}:{line_no}: unknown figure asset {src!r}")
    svg = (base / src).read_text()
    return (
        f'<figure class="figure">{svg}'
        f"<figcaption>{inline(caption)}</figcaption></figure>"
    )


def _para_breaks(stripped: str) -> bool:
    return (
        stripped.startswith(("#", ">", "|", "```", "---", "- ", "* ", "!["))
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
    parts.append('<div class="nav-group">Heritage</div>')
    parts.append(item("appendix-h-history.html", "A History in Convergents", "appendix-h-history"))
    parts.append('<div class="nav-group">Branch</div>')
    parts.append(item("appendix-i-branches.html", "Other Ways to Unfold", "appendix-i-branches"))
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
{THEME_BOOTSTRAP}
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="topbar">
  <button class="menu-btn" aria-label="Toggle navigation" onclick="document.body.classList.toggle('nav-open')">&#9776;</button>
  <a class="wordmark" href="index.html">Recursive Continuance <b>Tour&nbsp;Bus</b></a>
  <div class="search">
    <input id="search-input" type="search" placeholder="Search the tour" aria-label="Search the tour" autocomplete="off" spellcheck="false">
    <div class="search-results" id="search-results" hidden></div>
  </div>
  <button class="theme-toggle" id="theme-toggle" aria-label="Cycle color theme">Theme: Auto</button>
</header>
<div class="layout">
  <nav class="sidebar" aria-label="Route">{nav}</nav>
  <main class="content" id="main">{content}</main>
</div>
<footer class="site-footer">
  <span>Recursive Continuance Tour Bus &middot; a guided tour of recursion &amp; continued fractions</span>
  <span>Built from the <code>tourbus</code> engine &middot; <code>python -m tourbus</code></span>
</footer>
<script src="assets/search-index.js"></script>
<script src="assets/rct-docs.js"></script>
</body>
</html>
"""


# --------------------------------------------------------------------------- #
#  Landing page.
# --------------------------------------------------------------------------- #

def _express_sections(
    src: Path = DOCS / "appendix-d-frontier.md",
) -> list[tuple[str, str, str]]:
    """Parse Appendix D's ``## E...`` headings: (label, anchor, heading rest).

    Anchors reuse ``_slug`` on the same heading text ``md_to_html`` sees, so
    the landing cards can never drift from the generated ``id=`` attributes.
    """
    if not src.exists():
        return []
    out = []
    for m in re.finditer(r"^##\s+(E(\d+)\b[^\n]*)", src.read_text(), flags=re.M):
        heading = m.group(1).strip()
        rest = re.sub(r"^E\d+\s*[—–:-]*\s*", "", heading)
        out.append((f"E{m.group(2)}", _slug(heading), rest))
    return out


def _heritage_sections(
    src: Path = DOCS / "appendix-h-history.md",
) -> list[tuple[str, str, str]]:
    """Parse Appendix H's ``## H...`` headings: (label, anchor, heading rest).

    The Heritage clone of :func:`_express_sections`; interlude and
    front-matter headings are plain ``##`` text and cannot match.
    """
    if not src.exists():
        return []
    out = []
    for m in re.finditer(r"^##\s+(H(\d+)\b[^\n]*)", src.read_text(), flags=re.M):
        heading = m.group(1).strip()
        rest = re.sub(r"^H\d+\s*[—–:-]*\s*", "", heading)
        out.append((f"H{m.group(2)}", _slug(heading), rest))
    return out


def _branch_sections(
    src: Path = DOCS / "appendix-i-branches.md",
) -> list[tuple[str, str, str]]:
    """Parse Appendix I's ``## B...`` headings: (label, anchor, heading rest).

    The Branch clone of :func:`_express_sections`.
    """
    if not src.exists():
        return []
    out = []
    for m in re.finditer(r"^##\s+(B(\d+)\b[^\n]*)", src.read_text(), flags=re.M):
        heading = m.group(1).strip()
        rest = re.sub(r"^B\d+\s*[—–:-]*\s*", "", heading)
        out.append((f"B{m.group(2)}", _slug(heading), rest))
    return out


def _section_cards(
    sections: list[tuple[str, str, str]],
    curated: list[tuple[str, str]],
    page: str,
    cls: str,
) -> str:
    """Landing cards for parsed ``## X<n>`` sections plus curated blurbs."""
    cards = []
    for k, (label, anchor, rest) in enumerate(sections, start=1):
        if k <= len(curated):
            title, note = curated[k - 1]
        else:  # no curated blurb yet: derive card copy from the heading itself
            title, _, note = rest.partition(":")
            title, note = title.strip(), note.strip()
            if note:
                note = note[0].upper() + note[1:]
                note += "" if note.endswith((".", "!", "?")) else "."
        cards.append(
            f'<a class="card {cls}" href="{page}#{anchor}">'
            f'<span class="card-num">{label}</span>'
            f'<span class="card-title">{html.escape(title)}</span>'
            f'<span class="card-note">{html.escape(note)}</span></a>'
        )
    return "\n".join(cards)


def landing() -> str:
    tour_cards = "\n".join(
        f'<a class="card" href="{slug}.html"><span class="card-num">{k}</span>'
        f'<span class="card-title">{html.escape(title)}</span></a>'
        for k, (slug, title) in enumerate(STOPS, start=1)
    )
    sections = _express_sections()
    express_cards = _section_cards(sections, EXPRESS, "appendix-d-frontier.html", "express")
    h_sections = _heritage_sections()
    heritage_cards = _section_cards(h_sections, HERITAGE, "appendix-h-history.html", "heritage")
    b_sections = _branch_sections()
    branch_cards = _section_cards(b_sections, BRANCH, "appendix-i-branches.html", "branch")
    count_words = {6: "Six", 7: "Seven", 8: "Eight", 9: "Nine"}
    express_count = count_words.get(len(sections), str(len(sections)))
    heritage_count = count_words.get(len(h_sections), str(len(h_sections)))
    branch_count = count_words.get(len(b_sections), str(len(b_sections)))
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
  <p>{express_count} deeper, stranger stops past the terminus &mdash; each still computed
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
  <h2>The Heritage Line</h2>
  <p>{heritage_count} stops through twenty-three centuries of history &mdash;
  Euclid's mutual measuring, the chakravala, the first fractions in print,
  Huygens' gears, Lambert's proof, Liouville's built-to-order transcendental,
  the tree of Stern and Brocot, the factorization of F&#8327;, and Gosper's
  stream machine &mdash; every episode re-run live on the engine with
  <code>python -m tourbus heritage</code>. See
  <a href="appendix-h-history.html">Appendix H</a>.</p>
  <div class="card-grid">{heritage_cards}</div>
</section>

<section>
  <h2>The Branch Line</h2>
  <p>{branch_count} other ways to unfold a number &mdash; the Engel and Pierce
  staircases, the greedy Egyptian scribe, Zeckendorf's Fibonacci binary,
  Sturmian cutting sequences, and the exchange rate of Lochs' theorem &mdash;
  each an alternative to the continued fraction, computed exactly with
  <code>python -m tourbus branch</code>. See
  <a href="appendix-i-branches.html">Appendix I</a>.</p>
  <div class="card-grid">{branch_cards}</div>
</section>

<section>
  <h2>Reference &amp; running it</h2>
  <ul class="ref-list">
    <li><a href="appendix-a-proofs.html">Appendix A &mdash; Proofs</a></li>
    <li><a href="appendix-b-glossary.html">Appendix B &mdash; Glossary</a></li>
    <li><a href="appendix-c-references.html">Appendix C &mdash; References</a></li>
    <li><a href="appendix-g-hints.html">Appendix G &mdash; Hints &amp; selected answers</a></li>
    <li><a href="syllabus.html">The Syllabus &mdash; riding the tour as a course</a></li>
  </ul>
  <p>The whole tour is powered by <code>tourbus</code>, a standard-library-only
  Python package. Ride it in your terminal:</p>
  <pre><code>python -m tourbus            # the interactive tour
python -m tourbus --all      # the whole tour as a transcript
python -m tourbus frontier   # the Express Line
python -m tourbus heritage   # the Heritage Line (the history)
python -m tourbus branch     # the Branch Line (other expansions)
python -m tourbus demo gkw   # the Gauss-Kuzmin-Wirsing constant, from scratch</code></pre>
</section>
"""


# --------------------------------------------------------------------------- #
#  Build.
# --------------------------------------------------------------------------- #

def _with_toc(content: str) -> str:
    """Insert an "On this page" list after the h1 on pages with >= 4 h2s."""
    heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', content)
    if len(heads) < 4:
        return content
    items = []
    for hid, body in heads:
        label = re.sub(r"<[^>]+>", "", body)
        items.append(f'<li><a href="#{hid}">{label}</a></li>')
    toc = (
        '<nav class="page-toc" aria-label="On this page">'
        '<div class="toc-title">On this page</div>'
        f'<ol>{"".join(items)}</ol></nav>'
    )
    head, sep, tail = content.partition("</h1>")
    if sep:
        return head + sep + "\n" + toc + tail
    return toc + "\n" + content


def _plain(text: str) -> str:
    """Markdown/inline-HTML -> plain text, for the search index."""
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # italics first (the lookarounds skip ** runs) so nested **bold *italic*** resolves
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\*+", "", text)  # emphasis markers orphaned by snippet truncation
    return re.sub(r"\s+", " ", text).strip()


def _headings_with_snippets(text: str) -> list[dict[str, str]]:
    """Each h1-h3 of a Markdown page with a short plain-text snippet."""
    secs: list[dict[str, str]] = []
    raw: list[str] = []  # raw source lines of the current section's snippet
    in_code = False
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not stripped:
            continue
        m = re.match(r"^(#{1,3})\s+(.*)$", stripped)
        if m:
            secs.append({"id": _slug(m.group(2)), "t": _plain(m.group(2)), "s": ""})
            raw = []
            continue
        if (
            not secs
            or stripped.startswith(("#", "|", ">", "<", "!"))
            or stripped in ("---", "***", "___")
            or _is_nav_strip(stripped)
            or len(secs[-1]["s"]) >= 180
        ):
            continue
        candidate = re.sub(r"^(\d+\.|[-*])\s+", "", stripped)
        if _plain(candidate):
            # emphasis can span source lines: join the raw lines, then strip markers
            raw.append(candidate)
            secs[-1]["s"] = _plain(" ".join(raw))
    for sec in secs:
        if len(sec["s"]) > 180:
            sec["s"] = sec["s"][:177].rstrip() + "..."
    return secs


def _search_index(pages: list[tuple[str, str]]) -> str:
    """Build the client-side search index as a JS asset.

    A ``<script src>`` global (rather than fetched JSON) so search also works
    when the site is opened over ``file://``.
    """
    entries = []
    for slug, title in pages:
        src = DOCS / f"{slug}.md"
        if not src.exists():
            continue
        entries.append(
            {"p": f"{slug}.html", "t": title, "h": _headings_with_snippets(src.read_text())}
        )
    # The interactive exposition has no Markdown source; index its widget
    # sections by hand so search can reach them (ids resolve inside explore.html).
    entries.append({
        "p": "explore.html",
        "t": "Live Exposition",
        "h": [{"id": sid, "t": t, "s": s} for sid, t, s in EXPLORE_SECTIONS],
    })
    payload = json.dumps(entries, separators=(",", ":"), ensure_ascii=True)
    return f"window.RCT_SEARCH_INDEX={payload};\n"


def build() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    (DOCS / ".nojekyll").write_text("")
    (ASSETS / "rct-docs.css").write_text(CSS)
    (ASSETS / "rct-docs.js").write_text(JS)

    # chapters + express + reference
    pages = [(slug, title) for slug, title in STOPS]
    pages.append(("appendix-d-frontier", "The Express Line"))
    pages.append(("appendix-e-web-of-ideas", "The Web of Ideas"))
    pages.append(("appendix-f-cross-domain", "The Same Recurrence Everywhere"))
    pages.append(("appendix-h-history", "Appendix H - A History in Convergents"))
    pages.append(("appendix-i-branches", "Appendix I - The Branch Line"))
    pages += REFERENCE

    (ASSETS / "search-index.js").write_text(_search_index(pages))

    # teaching figures: emit every manifest entry, then prune strays so the
    # committed docs/assets/fig-*.svg set always equals the FIGURES manifest
    for name, fn in FIGURES.items():
        (ASSETS / name).write_text(fn())
    for orphan in sorted(ASSETS.glob("fig-*.svg")):
        if orphan.name not in FIGURES:
            orphan.unlink()
            print(f"  pruned orphan {orphan.name}")

    # landing
    (DOCS / "index.html").write_text(shell("Recursive Continuance Tour Bus", "index", landing()))

    for slug, title in pages:
        src = DOCS / f"{slug}.md"
        if not src.exists():
            print(f"  (skip missing {src.name})")
            continue
        content = _with_toc(md_to_html(src.read_text(), src_name=src.name))
        (DOCS / f"{slug}.html").write_text(shell(f"{title} - Tour Bus", slug, content))
        print(f"  wrote {slug}.html")

    # interactive exposition -> standalone doc
    expo = (ROOT / "site" / "index.html").read_text()
    standalone = _wrap_exposition(expo)
    (DOCS / "explore.html").write_text(standalone)
    print("  wrote explore.html (interactive exposition)")


def _wrap_exposition(fragment: str) -> str:
    """Make ``docs/explore.html`` from ``site/index.html``.

    A full standalone document (leading ``<!doctype``, any case) is copied
    through verbatim; a head-less fragment gets wrapped in a minimal shell,
    including the early theme-bootstrap script so the saved dark theme
    applies before first paint. Both paths are idempotent.
    """
    if fragment.lstrip().lower().startswith("<!doctype"):
        return fragment
    # The fragment starts with <title>...; give it a real head/body.
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<link rel=\"icon\" href=\"{FAVICON}\">\n"
        f"{THEME_BOOTSTRAP}\n"
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
/* the button anchors to a non-scrolling wrapper so it stays pinned while the <pre> scrolls */
.codewrap{position:relative}
.codewrap .copy-btn{position:absolute;top:.4rem;right:.4rem;font-family:var(--font-data);font-size:.62rem;
  text-transform:uppercase;letter-spacing:.05em;background:var(--surface);color:var(--ink-2);
  border:1px solid var(--border);border-radius:4px;padding:.25rem .5rem;cursor:pointer;
  opacity:0;transition:opacity .15s}
.codewrap:hover .copy-btn,.codewrap .copy-btn:focus-visible{opacity:1}
.codewrap .copy-btn:hover{border-color:var(--brass);color:var(--brass)}
@media (hover:none){.codewrap .copy-btn{opacity:1}}

/* skip link (visually hidden until focused) */
.skip-link{position:fixed;top:.5rem;left:.5rem;z-index:60;transform:translateY(-300%);
  background:var(--brass);color:#fff;font-family:var(--font-sign);font-weight:600;font-size:.85rem;
  padding:.5rem .8rem;border-radius:4px}
.skip-link:focus{transform:none}

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

/* search */
.search{position:relative;flex:0 1 230px;min-width:0}
.search input{width:100%;font-family:var(--font-data);font-size:.72rem;background:var(--surface);
  color:var(--ink);border:1px solid var(--border);border-radius:4px;padding:.4rem .55rem;line-height:1}
.search input::placeholder{color:var(--muted)}
.search input:focus{border-color:var(--brass)}
.search-results{position:absolute;top:calc(100% + 6px);right:0;width:min(430px,calc(100vw - 1.6rem));
  max-height:60vh;overflow-y:auto;background:var(--surface);border:1px solid var(--border);
  border-radius:5px;box-shadow:0 10px 26px rgba(0,0,0,.18);z-index:40;font-family:var(--font-sign)}
.search-hit{display:block;padding:.45rem .7rem;border-bottom:1px solid var(--border);color:var(--ink);
  font-size:.82rem}
.search-hit:last-child{border-bottom:none}
.search-hit:hover,.search-hit.active{background:color-mix(in srgb,var(--brass) 10%,transparent);
  text-decoration:none}
.hit-page{font-family:var(--font-data);font-size:.62rem;text-transform:uppercase;letter-spacing:.06em;
  color:var(--brass)}
.hit-head{font-weight:600}
.hit-snip{display:block;font-size:.72rem;color:var(--ink-2);white-space:nowrap;overflow:hidden;
  text-overflow:ellipsis}
.search-empty{padding:.5rem .7rem;font-size:.78rem;color:var(--muted)}

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

/* per-page "On this page" list */
.page-toc{margin:0 0 1.4rem;padding:.55rem .9rem .7rem;background:var(--surface);
  border:1px solid var(--border);border-radius:5px;font-family:var(--font-sign);font-size:.84rem}
.toc-title{font-family:var(--font-data);font-size:.64rem;text-transform:uppercase;letter-spacing:.12em;
  color:var(--muted);margin:.1rem 0 .3rem}
.page-toc ol{margin:0;padding-left:1.25rem}
.page-toc li{margin:.15rem 0}

/* figures + mermaid diagrams (both inlined SVG) */
.diagram{margin:1.6rem 0;text-align:center}
.diagram svg{max-width:100%;height:auto}
figure.figure{margin:1.6rem 0;text-align:center}
figure.figure svg{max-width:100%;height:auto;color:var(--ink)}
figure.figure figcaption{font-family:var(--font-sign);font-size:.82rem;color:var(--ink-2);margin-top:.4rem}

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
  .search{flex:1 1 120px}
  .page-toc{display:none}
}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}.card:hover{transform:none}
  .sidebar{transition:none}.codewrap .copy-btn{transition:none}}

/* print */
@media print{
  /* pin the palette so a persisted dark theme cannot leak into print output */
  :root,:root[data-theme="dark"],:root[data-theme="light"]{
    --page:#fff; --surface:#fff; --ink:#000; --ink-2:#333;
    --muted:#555; --grid:#ddd; --border:rgba(0,0,0,.25); --brass:#8a5a10;
  }
  .topbar,.sidebar,.site-footer,.skip-link,.page-toc,.chapter-nav,.search,.codewrap .copy-btn{display:none!important}
  body{background:#fff;color:#000}
  .layout{display:block;max-width:none}
  .content{max-width:none;padding:0}
  a{color:#000}
  code{background:none}
  pre{background:#fff;border-color:#999}
  pre,blockquote,.tablewrap,tr,.diagram,figure.figure{page-break-inside:avoid}
  h1,h2,h3,h4{page-break-after:avoid}
}
"""

JS = r"""(function(){
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

// copy buttons on code blocks
(function(){
  document.querySelectorAll('.content pre').forEach(function(pre){
    // wrap the scrollable <pre> so the button stays pinned while the code scrolls
    var wrap=document.createElement('div');
    wrap.className='codewrap';
    pre.parentNode.insertBefore(wrap,pre);
    wrap.appendChild(pre);
    var btn=document.createElement('button');
    btn.type='button';btn.className='copy-btn';btn.textContent='Copy';
    btn.addEventListener('click',function(){
      var text=(pre.querySelector('code')||pre).textContent;
      function done(){btn.textContent='Copied';setTimeout(function(){btn.textContent='Copy';},1500);}
      function fallback(){
        var ta=document.createElement('textarea');
        ta.value=text;ta.style.position='fixed';ta.style.opacity='0';
        document.body.appendChild(ta);ta.select();
        try{document.execCommand('copy');done();}catch(e){}
        document.body.removeChild(ta);
      }
      if(navigator.clipboard&&navigator.clipboard.writeText){
        navigator.clipboard.writeText(text).then(done,fallback);
      }else{fallback();}
    });
    wrap.appendChild(btn);
  });
})();

// client-side search over the build-time index (assets/search-index.js)
(function(){
  var input=document.getElementById('search-input');
  var box=document.getElementById('search-results');
  if(!input||!box)return;
  var hits=[],active=-1;
  function close(){box.hidden=true;box.innerHTML='';hits=[];active=-1;}
  function mark(i){
    var links=box.querySelectorAll('.search-hit');
    if(links[active])links[active].classList.remove('active');
    active=i;
    if(links[active]){links[active].classList.add('active');links[active].scrollIntoView({block:'nearest'});}
  }
  function esc(s){return s.replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function run(){
    var idx=window.RCT_SEARCH_INDEX||[];
    var q=input.value.trim().toLowerCase();
    close();
    if(q.length<2)return;
    var terms=q.split(/\s+/);
    for(var p=0;p<idx.length&&hits.length<12;p++){
      var pg=idx[p];
      for(var h=0;h<pg.h.length&&hits.length<12;h++){
        var sec=pg.h[h];
        var hay=(pg.t+' '+sec.t+' '+sec.s).toLowerCase();
        var ok=terms.every(function(t){return hay.indexOf(t)>=0;});
        if(ok)hits.push({href:pg.p+'#'+sec.id,page:pg.t,head:sec.t,snip:sec.s});
      }
    }
    if(!hits.length){box.innerHTML='<div class="search-empty">No matches.</div>';box.hidden=false;return;}
    box.innerHTML=hits.map(function(x){
      return '<a class="search-hit" href="'+esc(x.href)+'">'
        +'<span class="hit-page">'+esc(x.page)+'</span> &rsaquo; '
        +'<span class="hit-head">'+esc(x.head)+'</span>'
        +'<span class="hit-snip">'+esc(x.snip)+'</span></a>';
    }).join('');
    box.hidden=false;
  }
  input.addEventListener('input',run);
  input.addEventListener('keydown',function(e){
    if(box.hidden)return;
    var n=box.querySelectorAll('.search-hit').length;
    if(e.key==='ArrowDown'&&n){e.preventDefault();mark((active+1)%n);}
    else if(e.key==='ArrowUp'&&n){e.preventDefault();mark((active-1+n)%n);}
    else if(e.key==='Enter'&&n){
      e.preventDefault();
      var pick=box.querySelectorAll('.search-hit')[active>=0?active:0];
      if(pick)window.location.href=pick.getAttribute('href');
    }
    else if(e.key==='Escape'){close();input.blur();}
  });
  box.addEventListener('click',function(e){
    if(e.target.closest&&e.target.closest('.search-hit'))setTimeout(close,0);
  });
  document.addEventListener('click',function(e){
    if(!e.target.closest||!e.target.closest('.search'))close();
  });
})();
"""


if __name__ == "__main__":
    build()
    print("Site built under docs/. Enable GitHub Pages -> Deploy from branch -> /docs.")
