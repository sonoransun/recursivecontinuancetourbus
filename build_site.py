#!/usr/bin/env python3
"""Generate the GitHub Pages site under ``docs/`` from the Markdown chapters.

Static, self-contained HTML (plus one shared stylesheet and one script) with
the tour's "transit diagram meets mathematical drafting" identity: a sidebar
drawn as a route line, a station-sign header on every page, a sticky
"on this page" rail, light/dark themes, and the interactive exposition bundled
in as ``explore.html``.

The Markdown dialect is deliberately small and GitHub-compatible, so every
page reads well both here and on github.com:

* ```` ``` ```` fences with no language are math displays (one line) or aligned
  formula blocks (several lines); fences whose first line is ``$ python -m
  tourbus ...`` (or a bare ``python -m tourbus ...``) become terminal windows;
  ```` ```mermaid ```` fences are drawn to inline SVG by ``build_mermaid.py``.
* ``> [!NOTE]`` / ``[!TIP]`` / ``[!IMPORTANT]`` / ``[!WARNING]`` /
  ``[!CAUTION]`` blockquotes are GitHub alerts; here they become callouts.
* A block-level ``![caption](assets/fig-*.svg)`` inlines an engine-drawn figure.
* ``### Then — ...`` / ``### Now — ...`` / ``### Next — ...`` headings get the
  history / today / frontier tags of the "Then, now, next" sections.

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

SITE_NAME = "Recursive Continuance Tour Bus"
REPO_URL = "https://github.com/sonoransun/recursivecontinuancetourbus"

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

# One line of landing-card copy per stop, in route order.
STOP_BLURBS = [
    "Euclid's algorithm: the oldest recursion still in daily use.",
    "Euclid let loose on the real numbers: the continued fraction.",
    "The recurrence that turns quotients into convergents.",
    "All ones: φ, Fibonacci, and the most irrational number.",
    "Best approximation: calendars, gears, and 355/113.",
    "Periodic fractions are exactly the quadratic irrationals.",
    "Pell's equation, solved by one period of √d.",
    "Every positive fraction exactly once: the Stern–Brocot tree.",
    "e keeps a pattern; π keeps a secret.",
    "Gauss–Kuzmin, Khinchin, Lévy: the laws of the typical number.",
    "Gosper's exact arithmetic on infinite streams.",
    "Ackermann, the Y combinator, and McCarthy's 91.",
    "Fractals as fixed points; dimension as a fraction.",
    "Twelve notes, a broken RSA key, and Collatz.",
    "The questions nobody can answer yet.",
]

# The section of the interactive exposition (explore.html) that carries each
# stop's widget; every id must exist in site/index.html.
STOP_EXPLORE = [
    "stop-1-depot", "stop-2-road", "stop-3-engine", "stop-4-golden",
    "stop-5-overlook", "stop-6-loop", "stop-7-cattle", "stop-8-family",
    "stop-9-celebrity", "stop-10-casino", "stop-11-assembly", "stop-12-tower",
    "stop-13-mirrors", "stop-14-souvenir", "stop-15-terminus",
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
# match a "<section id=...>" in site/index.html so search hits resolve
# (tests/site/test_md.py checks every one).
EXPLORE_SECTIONS = [
    ("stop-1-depot", "Stop 1 - CF Expansion Machine (W1)",
     "Type a number or fraction and step Euclid's algorithm into its continued fraction; the convergents table updates live."),
    ("stop-4-golden", "Stop 4 - Golden Spiral & Irrationality Racer (W3, W4)",
     "The golden spiral at any depth and ratio, and a race of the convergent errors of phi, e, and pi."),
    ("stop-5-overlook", "Stop 5 - Calendar Designer (W9)",
     "Design a leap-year rule as a convergent of the tropical year, 0.242190 days."),
    ("stop-7-cattle", "Stop 7 - Pell Playground (W7)",
     "Enter d and watch the convergent at the period boundary light up as the fundamental solution of x^2 - d y^2 = 1."),
    ("stop-8-family", "Stop 8 - Stern-Brocot Explorer (W2)",
     "Descend the mediant tree left and right to locate any fraction in lowest terms."),
    ("stop-10-casino", "Stop 10 - Gauss Map Cobweb & Khinchin Lab (W5, W6)",
     "Iterate the Gauss map T(x) = {1/x} as a cobweb, and watch the geometric mean of partial quotients approach Khinchin's constant."),
    ("stop-13-mirrors", "Stop 13 - Fractal Lab (W8)",
     "Draw the Koch, dragon, Sierpinski, and Hilbert curves at any depth."),
    ("stop-14-souvenir", "Stop 14 - Temperament Studio, Wiener Attack, Collatz (W10, W11, W12)",
     "Musical temperament tables, a small-exponent RSA break by convergents, and the Collatz orbit plotter."),
    ("stop-encore-blocks", "Encore - Colliding Blocks Count Pi (W13)",
     "A mass ratio of 100^n makes two elastic blocks collide the digits of pi times."),
    ("stop-crossdomain-butterfly", "Cross-Domain - Hofstadter Butterfly (W14)",
     "The fractal spectrum of an electron in a magnetic field, drawn from continuant Sturm sequences versus flux p/q."),
    ("stop-branch-bazaar", "Branch - The Expansion Bazaar (W15)",
     "Enter one number and see it unfolded five ways at once: continued fraction, Engel, Pierce, greedy Egyptian, and Zeckendorf, with the error of each."),
]

REFERENCE = [
    ("appendix-a-proofs", "Appendix A — Proofs"),
    ("appendix-b-glossary", "Appendix B — Glossary"),
    ("appendix-c-references", "Appendix C — References"),
    ("appendix-g-hints", "Appendix G — Hints & selected answers"),
    ("syllabus", "Syllabus — for instructors"),
]

# The enrichment lines: (key, sidebar group label, page slug, link label).
LINE_PAGES = [
    ("express", "The Express Line", "appendix-d-frontier", "Fringe Avenues"),
    ("web", "Synthesis", "appendix-e-web-of-ideas", "The Web of Ideas"),
    ("cross", "Cross-Domain", "appendix-f-cross-domain", "The Same Recurrence"),
    ("heritage", "Heritage", "appendix-h-history", "A History in Convergents"),
    ("branch", "Branch", "appendix-i-branches", "Other Ways to Unfold"),
]

LINE_NAMES = {
    "main": "The Tour",
    "express": "The Express Line",
    "web": "Synthesis",
    "cross": "The Cross-Domain Line",
    "heritage": "The Heritage Line",
    "branch": "The Branch Line",
    "ref": "Reference",
}

# The command that rides each enrichment line, and its showcase widget.
LINE_RUN = {
    "express": "python -m tourbus frontier",
    "cross": "python -m tourbus crossdomain",
    "heritage": "python -m tourbus heritage",
    "branch": "python -m tourbus branch",
}
LINE_EXPLORE = {
    "express": "stop-encore-blocks",
    "cross": "stop-crossdomain-butterfly",
    "branch": "stop-branch-bazaar",
}

# Short labels for the prev/next pager, keyed by page slug.
PAGE_LABELS = {
    "appendix-d-frontier": "The Express Line",
    "appendix-e-web-of-ideas": "The Web of Ideas",
    "appendix-f-cross-domain": "The Cross-Domain Line",
    "appendix-h-history": "The Heritage Line",
    "appendix-i-branches": "The Branch Line",
    "appendix-a-proofs": "Appendix A · Proofs",
    "appendix-b-glossary": "Appendix B · Glossary",
    "appendix-c-references": "Appendix C · References",
    "appendix-g-hints": "Appendix G · Hints & answers",
    "syllabus": "The Syllabus",
}

# The landing page's "Then, now, next" sampler: (title, blurb, href, line).
# Each href points at a chapter's "Then, now, next" section.
TEASERS = [
    ("Inside every secure connection",
     "Euclid's extended algorithm computes the modular inverses behind RSA and "
     "elliptic-curve keys — today in constant time.",
     "01-depot.html#then-now-next"),
    ("The last step of Shor's algorithm",
     "A quantum computer measures a phase; a continued fraction turns it into the "
     "period that factors the modulus.",
     "14-souvenir-shop.html#then-now-next"),
    ("The calendar on your wall",
     "Leap-year rules are rational approximations, from Meton's 19-year cycle to the "
     "Gregorian compromise.",
     "05-scenic-overlook.html#then-now-next"),
    ("Quantum-easy, classically hard",
     "Pell's equation is one of the rare problems a quantum computer solves "
     "exponentially faster.",
     "07-cattle-crossing.html#then-now-next"),
    ("Inside union–find",
     "The inverse of Ackermann's function is the running time of one of computing's "
     "workhorse data structures.",
     "12-tower.html#then-now-next"),
    ("Near the Big Bang",
     "The Gauss map drives the chaotic oscillations of the BKL cosmological "
     "singularity.",
     "10-casino.html#then-now-next"),
    ("Mapping the planet",
     "Space-filling curves order geospatial indexes, database keys, and GPU memory.",
     "13-hall-of-mirrors.html#then-now-next"),
    ("Machines that conjecture",
     "Algorithms now hunt for new continued fractions of famous constants.",
     "09-celebrity.html#then-now-next"),
]

# The route logo (two stations joined by a curved line), shared by the tab
# icon and the wordmark; the same drawing the exposition uses.
FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E"
    "%3Cpath d='M24 78V52a26 26 0 0 1 26-26h26' fill='none' stroke='%23b5751a' "
    "stroke-width='11' stroke-linecap='round'/%3E"
    "%3Ccircle cx='24' cy='78' r='13' fill='%23b5751a'/%3E"
    "%3Ccircle cx='76' cy='26' r='13' fill='%23b5751a'/%3E%3C/svg%3E"
)
LOGO_SVG = (
    '<svg class="logo" viewBox="0 0 100 100" aria-hidden="true" focusable="false">'
    '<path d="M24 78V52a26 26 0 0 1 26-26h26" fill="none" stroke="currentColor" '
    'stroke-width="12" stroke-linecap="round"/>'
    '<circle cx="24" cy="78" r="14" fill="currentColor"/>'
    '<circle cx="76" cy="26" r="14" fill="currentColor"/></svg>'
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

# GitHub alert types -> (css modifier, site label).
_ALERTS = {
    "NOTE": ("note", "Note"),
    "TIP": ("tip", "Try it"),
    "IMPORTANT": ("key", "Key idea"),
    "WARNING": ("warn", "Watch out"),
    "CAUTION": ("caution", "Caution"),
}

_SHELL_LANGS = ("console", "shell", "sh", "bash")


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


def _terminal_html(buf: list[str]) -> str:
    """A transcript fence as a terminal window.

    ``$ `` lines are commands (prompt and command styled apart, a trailing
    ``  # comment`` dimmed); everything else is output, verbatim. A fence of
    bare ``python -m tourbus ...`` commands gets its prompts added.
    """
    lines = list(buf)
    while lines and not lines[-1].strip():
        lines.pop()
    bare = not any(ln.startswith("$ ") for ln in lines)
    rows = []
    for ln in lines:
        is_cmd = ln.startswith("$ ") or (bare and ln.strip() and not ln.lstrip().startswith("#"))
        if is_cmd:
            cmd = ln[2:] if ln.startswith("$ ") else ln
            body, hash_, comment = cmd.partition("  #")
            row = f'<span class="tp">$</span> <span class="tc">{html.escape(body.rstrip())}</span>'
            if hash_:
                pad = " " * (len(body) - len(body.rstrip()) + 2)
                row += f'{pad}<span class="tk">#{html.escape(comment)}</span>'
            rows.append(row)
        elif bare and ln.lstrip().startswith("#"):
            rows.append(f'<span class="tk">{html.escape(ln)}</span>')
        else:
            rows.append(html.escape(ln))
    return (
        '<div class="terminal"><div class="term-bar" aria-hidden="true">'
        '<i></i><i></i><i></i><span>tourbus</span></div>'
        f'<pre><code>{chr(10).join(rows)}</code></pre></div>'
    )


def _code_block(buf: list[str], lang: str) -> str:
    """Render one non-mermaid fence by kind: terminal, code, display, formula."""
    first = next((ln.strip() for ln in buf if ln.strip()), "")
    if lang in _SHELL_LANGS or (not lang and first.startswith(("$ ", "python -m "))):
        return _terminal_html(buf)
    if lang:
        return f'<pre><code class="lang-{lang}">{html.escape(chr(10).join(buf))}</code></pre>'
    content = [ln for ln in buf if ln.strip()]
    if len(content) == 1:
        # a single displayed formula, typeset in the reading face
        return f'<div class="math-display">{html.escape(content[0].strip())}</div>'
    return f'<pre class="formula"><code>{html.escape(chr(10).join(buf))}</code></pre>'


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
            out.append(_code_block(buf, lang))
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

        # blockquote, or a GitHub alert (> [!NOTE] ...) rendered as a callout
        if stripped.startswith(">"):
            raw = []
            while i < n and lines[i].strip().startswith(">"):
                raw.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            am = re.match(r"^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*$", raw[0].strip())
            if am:
                kind, label = _ALERTS[am.group(1)]
                inner = md_to_html("\n".join(raw[1:]), src_name=src_name)
                out.append(
                    f'<aside class="callout callout-{kind}" role="note">'
                    f'<p class="callout-title">{label}</p>{inner}</aside>'
                )
                continue
            paras: list[list[str]] = [[]]
            for r in raw:
                if r.strip():
                    paras[-1].append(r.strip())
                elif paras[-1]:
                    paras.append([])
            paras = [p for p in paras if p]
            if len(paras) <= 1:
                out.append(f"<blockquote>{inline(' '.join(paras[0] if paras else []))}</blockquote>")
            else:
                body = "".join(f"<p>{inline(' '.join(p))}</p>" for p in paras)
                out.append(f"<blockquote>{body}</blockquote>")
            continue

        # list (ordered or unordered), items may carry indented raw-HTML continuations
        if re.match(r"^(\d+\.|[-*])\s+", stripped):
            ordered = bool(re.match(r"^\d+\.", stripped))
            start = int(stripped.split(".")[0]) if ordered else 1
            items: list[str] = []
            while i < n:
                cur = lines[i]
                mm = re.match(r"^(\d+\.|[-*])\s+(.*)$", cur.strip())
                if mm and bool(re.match(r"^\d+\.", cur.strip())) == ordered:
                    items.append(mm.group(2))
                    i += 1
                elif cur.startswith(("  ", "\t")) and cur.strip():
                    items[-1] += " " + cur.strip()  # continuation of previous item
                    i += 1
                elif ordered and not cur.strip():
                    # a "loose" numbered list: blank lines between items keep
                    # the list (and its numbering) going
                    j = i
                    while j < n and not lines[j].strip():
                        j += 1
                    nm = re.match(r"^(\d+)\.\s+", lines[j].strip()) if j < n else None
                    if nm and int(nm.group(1)) == start + len(items):
                        i = j
                        continue
                    break
                else:
                    break
            tag = "ol" if ordered else "ul"
            attr = f' start="{start}"' if ordered and start != 1 else ""
            body = "".join(f"<li>{inline(it)}</li>" for it in items)
            out.append(f"<{tag}{attr}>{body}</{tag}>")
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
#  Page assembly: station-sign header, sections, rail, pager.
# --------------------------------------------------------------------------- #

def _page_line(slug: str) -> str:
    """The route line a page belongs to (drives its accent color)."""
    if slug in _STOP_INDEX:
        return "main"
    for key, _group, page, _label in LINE_PAGES:
        if page == slug:
            return key
    return "ref"


_STOP_INDEX = {slug: k for k, (slug, _t) in enumerate(STOPS, start=1)}


def _reading_order() -> list[str]:
    """Every generated page in the order a rider would take them."""
    order = [slug for slug, _t in STOPS]
    order += [page for _k, _g, page, _l in LINE_PAGES]
    order += [slug for slug, _t in REFERENCE]
    return order


def _page_label(slug: str) -> str:
    if slug in _STOP_INDEX:
        k = _STOP_INDEX[slug]
        return f"Stop {k} · {STOPS[k - 1][1]}"
    return PAGE_LABELS.get(slug, slug)


def _strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s)


def _split_head(body: str) -> tuple[tuple[str, str, str | None] | None, str]:
    """Pull the ``<h1>`` and its epigraph blockquote off the top of a page.

    Returns ``((h1_id, h1_inner_html, lede_html_or_None), rest)``. Markdown
    nav strips (the ``[← Prev] · [Route map] · [Next →]`` lines kept for
    GitHub readers) are dropped; the site draws its own crumbs and pager.
    """
    body = re.sub(r'<p class="chapter-nav">.*?</p>\n?', "", body)
    m = re.search(r'<h1 id="([^"]+)">(.*?)</h1>\n?', body)
    if not m:
        return None, body
    rest = body[: m.start()] + body[m.end():]
    lede = None
    bm = re.match(r"\s*<blockquote>((?:(?!</blockquote>).)*)</blockquote>\n?", rest[m.start():], flags=re.S)
    if bm and "<p>" not in bm.group(1):
        lede = bm.group(1)
        rest = rest[: m.start()] + rest[m.start() + bm.end():]
    return (m.group(1), m.group(2), lede), rest


def _title_parts(slug: str, heading: str) -> tuple[str, str]:
    """Split "Kicker — Title[: Subtitle]" into a kicker and a display title."""
    left, sep, right = heading.partition(" — ")
    if not sep:
        return "", heading
    if slug.startswith("appendix-") and ": " in right:
        a, _, b = right.partition(": ")
        return f"{left} · {a}", b
    return left, right


def _words(md: str) -> int:
    """Prose words in a Markdown page (fenced blocks excluded)."""
    prose = re.sub(r"```.*?```", " ", md, flags=re.S)
    return len(re.findall(r"[A-Za-z0-9']+", prose))


def _page_head(slug: str, head: tuple[str, str, str | None], md: str, body: str) -> str:
    hid, heading, lede = head
    line = _page_line(slug)
    kicker, title = _title_parts(slug, heading)
    k = _STOP_INDEX.get(slug)
    if k:
        roundel = f'<span class="roundel">{k}</span>'
        kick = f"Main line · Stop {k} of {len(STOPS)}"
    else:
        roundel = '<span class="roundel roundel-dot" aria-hidden="true"></span>'
        kick = kicker
    minutes = max(1, round(_words(md) / 230))
    meta = [f'<li><span class="mk">Reading</span> {minutes} min</li>']
    run = f"python -m tourbus stop {k}" if k else LINE_RUN.get(line)
    if run:
        meta.append(f'<li><span class="mk">Run it</span> <code>{html.escape(run)}</code></li>')
    widget = STOP_EXPLORE[k - 1] if k else LINE_EXPLORE.get(line)
    if widget:
        meta.append(f'<li><a class="mlink" href="explore.html#{widget}">Live widget&nbsp;&#8599;</a></li>')
    crumbs = (
        '<nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Route map</a>'
        f'<span aria-hidden="true">/</span><span>{html.escape(LINE_NAMES[line])}</span></nav>'
    )
    lede_html = f'<p class="lede">{lede}</p>' if lede else ""
    return (
        f'<header class="page-head">{crumbs}'
        f'<div class="kicker">{roundel}<span>{kick}</span></div>'
        f'<h1 id="{hid}">{title}</h1>{lede_html}'
        f'<ul class="page-meta">{"".join(meta)}</ul></header>'
    )


def _wrap_sections(body: str) -> str:
    """Wrap each ``<h2>`` and what follows it in a ``<section data-sec>``."""
    parts = re.split(r'(?=<h2 id=")', body)
    out = []
    for part in parts:
        m = re.match(r'<h2 id="([^"]+)">', part)
        if m:
            out.append(f'<section class="sec" data-sec="{m.group(1)}">\n{part.strip()}\n</section>')
        elif part.strip():
            out.append(f'<div class="intro">\n{part.strip()}\n</div>')
    return "\n".join(out)


_TNN = {"Then": "then", "Now": "now", "Next": "next"}


def _decorate_headings(body: str) -> str:
    """Permalink anchors on h2/h3, and Then/Now/Next tags on h3."""

    def rep(m: re.Match) -> str:
        lvl, hid, inner = m.group(1), m.group(2), m.group(3)
        tm = re.match(r"^(Then|Now|Next) — (.*)$", inner, flags=re.S)
        if lvl == "3" and tm:
            key = _TNN[tm.group(1)]
            rest = tm.group(2)
            rest = rest[:1].upper() + rest[1:]  # "Then — the oldest…" reads "The oldest…" beside its tag
            inner = (f'<span class="tnn tnn-{key}">{tm.group(1)}</span>'
                     f'<span class="tnn-sep"> — </span>{rest}')
        return (f'<h{lvl} id="{hid}">{inner}'
                f'<a class="h-anchor" href="#{hid}" aria-label="Link to this section">#</a></h{lvl}>')

    return re.sub(r'<h([23]) id="([^"]+)">(.*?)</h\1>', rep, body, flags=re.S)


def _difficulty_badges(body: str) -> str:
    """Turn the exercise ratings "(★)", "(★★)", "(★★★)" into badges."""
    names = {1: "warm-up", 2: "standard", 3: "challenge"}

    def rep(m: re.Match) -> str:
        k = len(m.group(1))
        return (f'<span class="diff diff-{k}" title="Difficulty: {names[k]}" '
                f'aria-label="Difficulty {k} of 3">{m.group(1)}</span>')

    pieces = re.split(r"(<pre[\s>].*?</pre>)", body, flags=re.S)
    for j in range(0, len(pieces), 2):
        pieces[j] = re.sub(r"(?:<strong>)?\((★{1,3})\)(?:</strong>)?", rep, pieces[j])
    return "".join(pieces)


def _toc_entries(body: str) -> list[tuple[str, str, list[tuple[str, str]]]]:
    """[(h2_id, label, [(h3_id, label), ...]), ...] in page order."""
    entries: list[tuple[str, str, list[tuple[str, str]]]] = []
    for m in re.finditer(r'<h([23]) id="([^"]+)">(.*?)</h\1>', body, flags=re.S):
        label = html.escape(html.unescape(_strip_tags(m.group(3))).strip(), quote=False)
        if m.group(1) == "2":
            entries.append((m.group(2), label, []))
        elif entries:
            entries[-1][2].append((m.group(2), label))
    if sum(1 + len(kids) for _i, _l, kids in entries) > 42:  # too tall: h2s only
        entries = [(i, lab, []) for i, lab, _k in entries]
    return entries


def _toc_html(entries, *, cls: str) -> str:
    items = []
    for hid, label, kids in entries:
        sub = ""
        if kids:
            sub = "<ol>" + "".join(f'<li><a href="#{k}">{lab}</a></li>' for k, lab in kids) + "</ol>"
        items.append(f'<li><a href="#{hid}">{label}</a>{sub}</li>')
    return f'<nav class="{cls}" aria-label="On this page"><div class="toc-title">On this page</div><ol>{"".join(items)}</ol></nav>'


def _az_index(body: str) -> str:
    """An A–Z jump bar for the glossary's ``### Term`` entries."""
    first: dict[str, str] = {}
    for m in re.finditer(r'<h3 id="([^"]+)">(.*?)</h3>', body, flags=re.S):
        text = html.unescape(_strip_tags(m.group(2))).strip()
        letter = text[:1].upper()
        if letter.isalpha() and letter not in first:
            first[letter] = m.group(1)
    links = "".join(f'<a href="#{hid}">{c}</a>' for c, hid in sorted(first.items()))
    return f'<nav class="az" aria-label="Glossary index">{links}</nav>'


def _pager(slug: str) -> str:
    order = _reading_order()
    if slug not in order:
        return ""
    k = order.index(slug)
    prev_slug = order[k - 1] if k > 0 else None
    next_slug = order[k + 1] if k + 1 < len(order) else None
    cells = []
    if prev_slug:
        cells.append(
            f'<a class="pager-prev" href="{prev_slug}.html"><span class="pager-dir">&#8592; Previous</span>'
            f'<span class="pager-title">{html.escape(_page_label(prev_slug))}</span></a>'
        )
    else:
        cells.append('<a class="pager-prev" href="index.html"><span class="pager-dir">&#8592; Back to</span>'
                     '<span class="pager-title">The route map</span></a>')
    if next_slug:
        cells.append(
            f'<a class="pager-next" href="{next_slug}.html"><span class="pager-dir">Next &#8594;</span>'
            f'<span class="pager-title">{html.escape(_page_label(next_slug))}</span></a>'
        )
    else:
        cells.append('<a class="pager-next" href="explore.html"><span class="pager-dir">Last stop &#8599;</span>'
                     '<span class="pager-title">The live exposition</span></a>')
    return f'<nav class="pager" aria-label="Previous and next page">{"".join(cells)}</nav>'


def _description(head, body: str) -> str:
    """A plain-text page summary for <meta name="description">."""
    text = head[2] if head and head[2] else ""
    if not text:
        pm = re.search(r"<p>(.*?)</p>", body, flags=re.S)
        text = pm.group(1) if pm else SITE_NAME
    text = re.sub(r"\s+", " ", html.unescape(_strip_tags(text))).strip()
    return text if len(text) <= 180 else text[:177].rstrip() + "..."


def page_content(slug: str, md: str, src_name: str) -> tuple[str, str, str, str]:
    """Render one Markdown page: (main html, rail html, description, title)."""
    raw = md_to_html(md, src_name=src_name)
    head, body = _split_head(raw)
    entries = _toc_entries(body)
    body = _wrap_sections(body)
    body = _decorate_headings(body)
    body = _difficulty_badges(body)
    if slug == "appendix-b-glossary":
        body = body.replace('<div class="intro">', '<div class="intro">' + _az_index(body), 1)
    rail = ""
    inline_toc = ""
    if len(entries) >= 3:
        rail = f'<aside class="toc-rail">{_toc_html(entries, cls="page-toc")}</aside>'
        inline_toc = (
            '<details class="toc-inline"><summary>On this page</summary>'
            f'{_toc_html(entries, cls="page-toc")}</details>'
        )
    header = _page_head(slug, head, md, body) if head else ""
    content = header + inline_toc + body + _pager(slug)
    title = SITE_NAME
    if head:
        kicker, t = _title_parts(slug, head[1])
        t = html.unescape(_strip_tags(t))
        kick = html.unescape(_strip_tags(kicker))
        title = f"{t} — {kick} · Tour Bus" if kick else f"{t} · Tour Bus"
    return content, rail, _description(head, body), title


# --------------------------------------------------------------------------- #
#  Page shell + navigation.
# --------------------------------------------------------------------------- #

def nav_html(active: str) -> str:
    def item(href: str, label: str, slug: str) -> str:
        cls = ' class="on"' if slug == active else ""
        return f'<a{cls} href="{href}">{html.escape(label)}</a>'

    parts = ['<a class="nav-home' + (' on' if active == "index" else "") + '" href="index.html">Route map</a>']
    parts.append('<div class="nav-sec" data-line="main"><div class="nav-group">The Tour</div><ol class="nav-line">')
    for k, (slug, title) in enumerate(STOPS, start=1):
        on = " on" if slug == active else ""
        cur = ' aria-current="page"' if slug == active else ""
        parts.append(
            f'<li><a class="stn{on}" href="{slug}.html"{cur}><span class="stn-n">{k}</span>'
            f'<span class="stn-t">{html.escape(title)}</span></a></li>'
        )
    parts.append("</ol></div>")
    for key, group, page, label in LINE_PAGES:
        parts.append(f'<div class="nav-sec" data-line="{key}"><div class="nav-group">{group}</div>')
        parts.append(item(f"{page}.html", label, page))
        parts.append("</div>")
    parts.append('<div class="nav-sec" data-line="ref"><div class="nav-group">Reference</div>')
    for slug, title in REFERENCE:
        parts.append(item(f"{slug}.html", title, slug))
    parts.append("</div>")
    parts.append('<div class="nav-sec" data-line="explore"><div class="nav-group">Interactive</div>')
    parts.append(item("explore.html", "Live Exposition ↗", "explore"))
    parts.append("</div>")
    return "\n".join(parts)


def _footer() -> str:
    lines = "".join(
        f'<a href="{page}.html">{html.escape(LINE_NAMES[key] if key != "web" else "The Web of Ideas")}</a>'
        for key, _g, page, _l in LINE_PAGES
    )
    return f"""<footer class="site-footer">
  <div class="foot-inner">
    <div class="foot-brand">
      <a class="wordmark" href="index.html">{LOGO_SVG}<span>Recursive Continuance <b>Tour&nbsp;Bus</b></span></a>
      <p>A guided tour of recursion and continued fractions. Every number on these pages was
      computed, exactly, by the <code>tourbus</code> engine: standard-library Python, no dependencies.</p>
    </div>
    <div class="foot-col"><div class="foot-h">Ride</div>
      <a href="01-depot.html">Board at the Depot</a><a href="explore.html">Live exposition</a>
      <a href="syllabus.html">Syllabus for instructors</a><a href="appendix-c-references.html">Reading list</a></div>
    <div class="foot-col"><div class="foot-h">Lines</div>{lines}</div>
    <div class="foot-col"><div class="foot-h">Project</div>
      <a href="{REPO_URL}">Source on GitHub</a><span>MIT licensed</span><span><code>python -m tourbus</code></span></div>
  </div>
</footer>"""


def shell(title: str, active: str, content: str, *, line: str = "main",
          rail: str = "", desc: str = "") -> str:
    nav = nav_html(active)
    desc = desc or "A guided tour of recursion and continued fractions, computed exactly."
    layout_cls = "layout has-rail" if rail else "layout"
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="auto">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#eceef1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0b0e13" media="(prefers-color-scheme: dark)">
<link rel="icon" href="{FAVICON}">
<link rel="stylesheet" href="assets/rct-docs.css">
{THEME_BOOTSTRAP}
</head>
<body data-line="{line}" data-page="{html.escape(active)}">
<div class="progress" aria-hidden="true"><i></i></div>
<a class="skip-link" href="#main">Skip to content</a>
<header class="topbar">
  <button class="menu-btn" type="button" aria-label="Toggle navigation" aria-controls="sidebar" aria-expanded="false">&#9776;</button>
  <a class="wordmark" href="index.html">{LOGO_SVG}<span>Recursive Continuance <b>Tour&nbsp;Bus</b></span></a>
  <div class="search">
    <input id="search-input" type="search" placeholder="Search the tour" aria-label="Search the tour" autocomplete="off" spellcheck="false">
    <kbd class="search-kbd" aria-hidden="true">/</kbd>
    <div class="search-results" id="search-results" hidden></div>
  </div>
  <a class="top-link" href="{REPO_URL}">GitHub</a>
  <button class="theme-toggle" id="theme-toggle" type="button" aria-label="Cycle color theme"><span class="tt-icon" aria-hidden="true"></span><span class="tt-label">Auto</span></button>
</header>
<div class="{layout_cls}">
  <nav class="sidebar" id="sidebar" aria-label="Route">{nav}</nav>
  <main class="content" id="main">{content}</main>
  {rail}
</div>
{_footer()}
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


def _cf_html(terms: list[str], tail: str = "⋱") -> str:
    """Typeset ``[a0; a1, a2, ...]`` as nested stacked fractions (HTML/CSS)."""
    inner = f'<span class="cf-tail">{tail}</span>'
    for a in reversed(terms[1:]):
        inner = (f'<span class="cf-term">{a}&#8202;+</span>'
                 f'<span class="cf-frac"><span class="cf-num">1</span>'
                 f'<span class="cf-den">{inner}</span></span>')
    return (f'<span class="cf-term">{terms[0]}&#8202;+</span>'
            f'<span class="cf-frac"><span class="cf-num">1</span>'
            f'<span class="cf-den">{inner}</span></span>')


def _counts() -> dict[str, int]:
    """Live counts for the landing statistics band."""
    expo = (ROOT / "site" / "index.html").read_text()
    try:
        from tourbus.tour.demos import DEMOS
        demos = len(DEMOS)
    except Exception:  # pragma: no cover - the engine is always importable here
        demos = 0
    try:
        from tourbus.tour.crossline import CROSS_STOPS
        cross = len(CROSS_STOPS)
    except Exception:  # pragma: no cover
        cross = 0
    return {
        "stops": len(STOPS),
        "express": len(_express_sections()),
        "heritage": len(_heritage_sections()),
        "branch": len(_branch_sections()),
        "cross": cross,
        "figures": len(FIGURES),
        "widgets": len(set(re.findall(r"function mountW(\d+)\(", expo))),
        "demos": demos,
    }


def landing() -> str:
    tour_cards = "\n".join(
        f'<a class="card stop" href="{slug}.html"><span class="card-num">{k}</span>'
        f'<span class="card-title">{html.escape(title)}</span>'
        f'<span class="card-note">{html.escape(STOP_BLURBS[k - 1])}</span></a>'
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
    teasers = "\n".join(
        f'<a class="card teaser" href="{href}"><span class="card-title">{html.escape(t)}</span>'
        f'<span class="card-note">{html.escape(b)}</span></a>'
        for t, b, href in TEASERS
    )
    c = _counts()
    stats = "".join(
        f'<div class="stat"><b>{v}</b><span>{html.escape(label)}</span></div>'
        for v, label in (
            (c["stops"], "stops on the main line"),
            (c["express"] + c["heritage"] + c["branch"] + c["cross"], "more on four branch lines"),
            (c["demos"], "runnable demonstrations"),
            (c["widgets"], "live widgets"),
            (c["figures"], "engine-drawn figures"),
            (0, "runtime dependencies"),
        )
    )
    network = FIGURES["fig-network.svg"]()
    cf = _cf_html(["3", "7", "15", "1", "292"])
    return f"""
<section class="hero">
  <div class="hero-grid">
    <div class="hero-copy">
      <div class="eyebrow">Line R &middot; Recursion &amp; Continued Fractions</div>
      <h1 class="hero-title">Recursive Continuance <span>Tour Bus</span></h1>
      <p class="tagline">A guided ride through the numbers that describe themselves &mdash; from
      Euclid's leftovers to Gosper's stream arithmetic, from Huygens' planetarium to the last
      step of a quantum algorithm, every result computed exactly by one small engine.</p>
      <div class="cta-row">
        <a class="cta primary" href="01-depot.html">Board at the Depot &nbsp;&#8594;</a>
        <a class="cta" href="explore.html">Open the live exposition &nbsp;&#8599;</a>
      </div>
    </div>
    <figure class="hero-cf" aria-label="pi as a continued fraction: 3 plus 1 over 7 plus 1 over 15 plus 1 over 1 plus 1 over 292, and so on">
      <div class="cf" aria-hidden="true"><span class="cf-lhs">&pi;&#8202;=</span>{cf}</div>
      <figcaption>Stop just before the <b>292</b> and you hold <b>355/113</b> &mdash; six correct
      decimals from a three-digit denominator. <a href="05-scenic-overlook.html">Why&nbsp;&#8594;</a></figcaption>
    </figure>
  </div>
  <div class="stats">{stats}</div>
</section>

<section class="band">
  <h2 id="the-network">The network</h2>
  <p>One main line of fifteen stops and four lines branching off it: the Heritage Line
  back through history, the Branch Line to the other ways of unfolding a number, the
  Cross-Domain Line into the sciences, and the Express Line past the terminus to the
  research frontier.</p>
  <figure class="figure network">{network}<figcaption>Every station is a chapter section
  and every one runs live: <code>python -m tourbus</code>, <code>heritage</code>,
  <code>branch</code>, <code>crossdomain</code>, <code>frontier</code>.</figcaption></figure>
</section>

<section class="band" data-line="main">
  <h2 id="the-tour">The Tour</h2>
  <p>Fifteen numbered stops, each with a chapter here, a live section in the
  interactive exposition, and a command-line demonstration you can run with
  <code>python -m tourbus stop N</code>.</p>
  <div class="card-grid">{tour_cards}</div>
</section>

<section class="band">
  <h2 id="then-now-next">Then, now, next</h2>
  <p>Every stop closes with its history, where the idea is at work today, and the
  open road ahead. A sampler of where two-thousand-year-old mathematics turns up now:</p>
  <div class="card-grid teasers">{teasers}</div>
</section>

<section class="band" data-line="express">
  <h2 id="the-express-line">The Express Line</h2>
  <p>{express_count} deeper, stranger stops past the terminus &mdash; each still computed
  exactly (or rigorously) on the same engine. See
  <a href="appendix-d-frontier.html">the Fringe Avenues</a>.</p>
  <div class="card-grid">{express_cards}</div>
</section>

<section class="band" data-line="heritage">
  <h2 id="the-heritage-line">The Heritage Line</h2>
  <p>{heritage_count} stops through twenty-three centuries of history &mdash;
  Euclid's mutual measuring, the chakravala, the first fractions in print,
  Huygens' gears, Lambert's proof, Liouville's built-to-order transcendental,
  the tree of Stern and Brocot, the factorization of F&#8327;, and Gosper's
  stream machine &mdash; every episode re-run live on the engine with
  <code>python -m tourbus heritage</code>. See
  <a href="appendix-h-history.html">Appendix H</a>.</p>
  <div class="card-grid">{heritage_cards}</div>
</section>

<section class="band" data-line="branch">
  <h2 id="the-branch-line">The Branch Line</h2>
  <p>{branch_count} other ways to unfold a number &mdash; the Engel and Pierce
  staircases, the greedy Egyptian scribe, Zeckendorf's Fibonacci binary,
  Sturmian cutting sequences, and the exchange rate of Lochs' theorem &mdash;
  each an alternative to the continued fraction, computed exactly with
  <code>python -m tourbus branch</code>. See
  <a href="appendix-i-branches.html">Appendix I</a>.</p>
  <div class="card-grid">{branch_cards}</div>
</section>

<section class="band duo">
  <a class="panel" data-line="cross" href="appendix-f-cross-domain.html">
    <span class="panel-kicker">The Cross-Domain Line</span>
    <span class="panel-title">The same recurrence everywhere</span>
    <span class="panel-body">The continuant behind every convergent is also a molecule's energy
    levels, the Hofstadter butterfly, a circuit's impedance, a control loop's stability, and a
    resummed divergent series; the golden ratio, meanwhile, arranges sunflowers and quasicrystals.
    Every claim runs live with <code>python -m tourbus crossdomain</code>.</span>
    <span class="panel-go">Ride the line &#8594;</span>
  </a>
  <a class="panel" data-line="web" href="appendix-e-web-of-ideas.html">
    <span class="panel-kicker">Synthesis</span>
    <span class="panel-title">The web of ideas</span>
    <span class="panel-body">Recursion, continued fractions, &pi;, and physics as one gesture
    &mdash; <em>the infinite defined by finite self-application</em>: fixed points and the Y
    combinator, the Gauss map as renormalization, the golden ratio as the most stable orbit, the
    devil's staircase, and two blocks that collide exactly &pi; times.</span>
    <span class="panel-go">Read the synthesis &#8594;</span>
  </a>
</section>

<section class="band">
  <h2 id="reference-running-it">Reference &amp; running it</h2>
  <ul class="ref-list">
    <li><a href="appendix-a-proofs.html">Appendix A &mdash; Proofs</a></li>
    <li><a href="appendix-b-glossary.html">Appendix B &mdash; Glossary</a></li>
    <li><a href="appendix-c-references.html">Appendix C &mdash; References</a></li>
    <li><a href="appendix-g-hints.html">Appendix G &mdash; Hints &amp; selected answers</a></li>
    <li><a href="syllabus.html">The Syllabus &mdash; riding the tour as a course</a></li>
  </ul>
  <p>The whole tour is powered by <code>tourbus</code>, a standard-library-only
  Python package. Ride it in your terminal:</p>
  {_terminal_html([
      "python -m tourbus            # the interactive tour",
      "python -m tourbus --all      # the whole tour as a transcript",
      "python -m tourbus frontier   # the Express Line",
      "python -m tourbus heritage   # the Heritage Line (the history)",
      "python -m tourbus branch     # the Branch Line (other expansions)",
      "python -m tourbus demo gkw   # the Gauss-Kuzmin-Wirsing constant, from scratch",
  ])}
</section>
"""


# --------------------------------------------------------------------------- #
#  Search index.
# --------------------------------------------------------------------------- #

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


# --------------------------------------------------------------------------- #
#  Build.
# --------------------------------------------------------------------------- #

def build() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    (DOCS / ".nojekyll").write_text("")
    (ASSETS / "rct-docs.css").write_text(CSS)
    (ASSETS / "rct-docs.js").write_text(JS)

    # chapters + the lines + reference
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
    (DOCS / "index.html").write_text(
        shell(f"{SITE_NAME} — a guided tour of recursion and continued fractions", "index",
              landing(), line="main",
              desc="A guided tour of recursion and continued fractions, from Euclid to the "
                   "research frontier, every result computed exactly by one small engine.")
    )

    for slug, _title in pages:
        src = DOCS / f"{slug}.md"
        if not src.exists():
            print(f"  (skip missing {src.name})")
            continue
        content, rail, desc, title = page_content(slug, src.read_text(), src.name)
        (DOCS / f"{slug}.html").write_text(
            shell(title, slug, content, line=_page_line(slug), rail=rail, desc=desc)
        )
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

CSS = r"""/* Recursive Continuance Tour Bus - GitHub Pages docs (generated by build_site.py) */

/* ---------- tokens ---------- */
:root{
  --page:#eceef1; --surface:#fafbfc; --surface-2:#f3f5f8; --ink:#12161c; --ink-2:#4a525c;
  --muted:#7d8792; --grid:#dbe0e6; --border:rgba(18,22,28,.11); --border-2:rgba(18,22,28,.2);
  --brass:#b5751a; --link:#99600c; --s1:#2a78d6; --s2:#1baf7a; --s3:#c8860f; --s5:#4a3aa7; --s6:#d1483f;
  --term-bg:#11161d; --term-bar:#1a2029; --term-ink:#dbe2ea; --term-dim:#8792a0; --term-cmd:#f3c16b;
  --shadow:0 1px 2px rgba(16,22,30,.05),0 8px 22px rgba(16,22,30,.07);
  --font-sign:ui-sans-serif,-apple-system,"Helvetica Neue",Helvetica,Arial,sans-serif;
  --font-read:"Iowan Old Style","Charter","Bitstream Charter","Palatino Linotype",Georgia,serif;
  --font-data:ui-monospace,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;
  --accent:var(--brass); --top:52px;
}
@media (prefers-color-scheme:dark){:root{
  --page:#0b0e13; --surface:#12171f; --surface-2:#161c25; --ink:#eef2f7; --ink-2:#aeb7c2;
  --muted:#707a86; --grid:#1c232d; --border:rgba(238,242,247,.1); --border-2:rgba(238,242,247,.2);
  --brass:#e0a63e; --link:#e8b252; --s1:#4b93e6; --s2:#22b183; --s3:#e0a63e; --s5:#9085e9; --s6:#e5675c;
  --term-bg:#070a0e; --term-bar:#11161d;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 10px 26px rgba(0,0,0,.35);
}}
:root[data-theme="light"]{
  --page:#eceef1; --surface:#fafbfc; --surface-2:#f3f5f8; --ink:#12161c; --ink-2:#4a525c;
  --muted:#7d8792; --grid:#dbe0e6; --border:rgba(18,22,28,.11); --border-2:rgba(18,22,28,.2);
  --brass:#b5751a; --link:#99600c; --s1:#2a78d6; --s2:#1baf7a; --s3:#c8860f; --s5:#4a3aa7; --s6:#d1483f;
  --term-bg:#11161d; --term-bar:#1a2029;
  --shadow:0 1px 2px rgba(16,22,30,.05),0 8px 22px rgba(16,22,30,.07);
}
:root[data-theme="dark"]{
  --page:#0b0e13; --surface:#12171f; --surface-2:#161c25; --ink:#eef2f7; --ink-2:#aeb7c2;
  --muted:#707a86; --grid:#1c232d; --border:rgba(238,242,247,.1); --border-2:rgba(238,242,247,.2);
  --brass:#e0a63e; --link:#e8b252; --s1:#4b93e6; --s2:#22b183; --s3:#e0a63e; --s5:#9085e9; --s6:#e5675c;
  --term-bg:#070a0e; --term-bar:#11161d;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 10px 26px rgba(0,0,0,.35);
}
/* each route line has a color; a page takes its line's color as its accent */
:root{--line-main:var(--brass); --line-express:var(--s5); --line-heritage:var(--s6);
  --line-branch:var(--s2); --line-cross:var(--s1); --line-web:var(--s3); --line-ref:var(--muted);
  --line-explore:var(--brass)}
[data-line="express"]{--accent:var(--line-express)}
[data-line="heritage"]{--accent:var(--line-heritage)}
[data-line="branch"]{--accent:var(--line-branch)}
[data-line="cross"]{--accent:var(--line-cross)}
[data-line="web"]{--accent:var(--line-web)}
[data-line="ref"]{--accent:var(--line-ref)}
[data-line="main"]{--accent:var(--line-main)}

/* ---------- base ---------- */
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:calc(var(--top) + 18px)}
body{margin:0;background:var(--page);color:var(--ink);font-family:var(--font-read);
  font-size:17.5px;line-height:1.7;-webkit-text-size-adjust:100%;text-rendering:optimizeLegibility;
  font-kerning:normal}
::selection{background:color-mix(in srgb,var(--brass) 28%,transparent)}
:focus-visible{outline:2px solid var(--brass);outline-offset:2px;border-radius:3px}
a{color:var(--link);text-decoration:underline;text-decoration-thickness:1px;
  text-underline-offset:.18em;text-decoration-color:color-mix(in srgb,var(--link) 35%,transparent)}
a:hover{text-decoration-color:currentColor}
code{font-family:var(--font-data);font-size:.84em;background:color-mix(in srgb,var(--brass) 10%,transparent);
  padding:.08em .34em;border-radius:4px;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}
pre{background:var(--surface);border:1px solid var(--border);border-radius:8px;
  padding:.95rem 1.05rem;overflow-x:auto;font-size:.8rem;line-height:1.6}
pre code{background:none;padding:0;font-size:inherit;line-height:inherit;overflow-wrap:normal}
kbd{font-family:var(--font-data);font-size:.7rem;border:1px solid var(--border-2);border-bottom-width:2px;
  border-radius:4px;padding:.05rem .35rem;color:var(--ink-2);background:var(--surface)}
.skip-link{position:fixed;top:.5rem;left:.5rem;z-index:80;transform:translateY(-300%);
  background:var(--brass);color:#fff;font-family:var(--font-sign);font-weight:600;font-size:.85rem;
  padding:.5rem .8rem;border-radius:6px;text-decoration:none}
.skip-link:focus{transform:none}

/* ---------- reading progress ---------- */
.progress{position:fixed;top:0;left:0;right:0;height:3px;z-index:70;pointer-events:none}
.progress i{display:block;height:100%;width:0;background:var(--accent);transition:width .08s linear}

/* ---------- top bar ---------- */
.topbar{position:sticky;top:0;z-index:40;display:flex;align-items:center;gap:.75rem;height:var(--top);
  padding:0 clamp(.8rem,2.4vw,1.4rem);background:color-mix(in srgb,var(--page) 86%,transparent);
  backdrop-filter:saturate(1.4) blur(10px);-webkit-backdrop-filter:saturate(1.4) blur(10px);
  border-bottom:1px solid var(--border)}
.wordmark{display:inline-flex;align-items:center;gap:.55rem;font-family:var(--font-sign);font-weight:800;
  font-size:.78rem;text-transform:uppercase;letter-spacing:.06em;color:var(--ink);text-decoration:none;
  margin-right:auto;white-space:nowrap}
.wordmark b{color:var(--brass)}
.wordmark .logo{width:22px;height:22px;color:var(--brass);flex:none}
.top-link{font-family:var(--font-sign);font-size:.8rem;font-weight:600;color:var(--ink-2);text-decoration:none}
.top-link:hover{color:var(--brass)}
.theme-toggle,.menu-btn{display:inline-flex;align-items:center;gap:.4rem;font-family:var(--font-data);
  font-size:.68rem;text-transform:uppercase;letter-spacing:.06em;background:var(--surface);color:var(--ink);
  border:1px solid var(--border);padding:.42rem .6rem;border-radius:6px;cursor:pointer;line-height:1}
.theme-toggle:hover,.menu-btn:hover{border-color:var(--brass);color:var(--brass)}
.tt-icon{width:.8rem;height:.8rem;border-radius:50%;border:1.5px solid currentColor;
  background:linear-gradient(90deg,currentColor 50%,transparent 50%)}
.theme-toggle[data-mode="light"] .tt-icon{background:transparent}
.theme-toggle[data-mode="dark"] .tt-icon{background:currentColor}
.menu-btn{display:none;font-size:1rem}

/* ---------- search ---------- */
.search{position:relative;flex:0 1 250px;min-width:0}
.search input{width:100%;font-family:var(--font-data);font-size:.74rem;background:var(--surface);
  color:var(--ink);border:1px solid var(--border);border-radius:6px;padding:.45rem 1.9rem .45rem .6rem;line-height:1}
.search input::placeholder{color:var(--muted)}
.search input:focus{border-color:var(--brass);outline:none;box-shadow:0 0 0 3px color-mix(in srgb,var(--brass) 18%,transparent)}
.search-kbd{position:absolute;right:.45rem;top:50%;transform:translateY(-50%);pointer-events:none}
.search input:focus ~ .search-kbd{display:none}
.search-results{position:absolute;top:calc(100% + 8px);right:0;width:min(460px,calc(100vw - 1.6rem));
  max-height:64vh;overflow-y:auto;background:var(--surface);border:1px solid var(--border);
  border-radius:10px;box-shadow:var(--shadow);z-index:50;font-family:var(--font-sign);padding:.3rem}
.search-hit{display:block;padding:.5rem .65rem;border-radius:7px;color:var(--ink);font-size:.84rem;text-decoration:none}
.search-hit:hover,.search-hit.active{background:color-mix(in srgb,var(--brass) 11%,transparent)}
.hit-page{font-family:var(--font-data);font-size:.62rem;text-transform:uppercase;letter-spacing:.06em;color:var(--brass)}
.hit-head{font-weight:650}
.hit-snip{display:block;font-size:.74rem;color:var(--ink-2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.search-empty{padding:.55rem .7rem;font-size:.8rem;color:var(--muted)}

/* ---------- layout ---------- */
.layout{display:grid;grid-template-columns:268px minmax(0,1fr);max-width:1180px;margin:0 auto;align-items:start}
.layout.has-rail{grid-template-columns:268px minmax(0,1fr) 232px;max-width:1440px}
.sidebar{position:sticky;top:var(--top);align-self:start;max-height:calc(100vh - var(--top));overflow-y:auto;
  padding:1.3rem .9rem 2.4rem 1rem;font-family:var(--font-sign);font-size:.85rem;scrollbar-width:thin}
.content{padding:2rem clamp(1.1rem,4vw,3.2rem) 4rem;min-width:0;max-width:48.5rem;width:100%;justify-self:center}
.toc-rail{position:sticky;top:calc(var(--top) + 1.2rem);align-self:start;max-height:calc(100vh - var(--top) - 2.4rem);
  overflow-y:auto;padding:1.2rem 1rem 2rem 0;scrollbar-width:thin}

/* ---------- sidebar: the route line ---------- */
.nav-home{display:block;font-weight:750;color:var(--ink);text-decoration:none;padding:.35rem .6rem;
  border-radius:6px;margin-bottom:.4rem}
.nav-home:hover,.nav-home.on{background:color-mix(in srgb,var(--brass) 10%,transparent);color:var(--brass)}
.nav-group{font-family:var(--font-data);font-size:.62rem;text-transform:uppercase;letter-spacing:.13em;
  color:var(--muted);margin:1.1rem 0 .35rem .6rem;display:flex;align-items:center;gap:.5rem}
.nav-group::before{content:"";width:14px;height:4px;border-radius:2px;background:var(--line-ref)}
.nav-sec[data-line="main"] .nav-group::before{background:var(--line-main)}
.nav-sec[data-line="express"] .nav-group::before{background:var(--line-express)}
.nav-sec[data-line="web"] .nav-group::before{background:var(--line-web)}
.nav-sec[data-line="cross"] .nav-group::before{background:var(--line-cross)}
.nav-sec[data-line="heritage"] .nav-group::before{background:var(--line-heritage)}
.nav-sec[data-line="branch"] .nav-group::before{background:var(--line-branch)}
.nav-sec[data-line="explore"] .nav-group::before{background:linear-gradient(90deg,var(--line-main),var(--line-express),var(--line-heritage),var(--line-branch))}
.nav-sec > a{display:block;padding:.3rem .6rem;border-radius:6px;color:var(--ink-2);text-decoration:none;
  border-left:3px solid transparent}
.nav-sec > a:hover{background:color-mix(in srgb,var(--brass) 8%,transparent);color:var(--ink)}
.nav-sec > a.on{color:var(--ink);font-weight:650;background:color-mix(in srgb,var(--accent) 12%,transparent);
  border-left-color:var(--accent)}
.nav-line{list-style:none;margin:0;padding:0;position:relative}
.nav-line::before{content:"";position:absolute;left:calc(.6rem + 10px);top:.8rem;bottom:.8rem;width:4px;
  margin-left:-2px;border-radius:2px;background:var(--line-main)}
.stn{display:flex;align-items:center;gap:.6rem;padding:.22rem .6rem;border-radius:6px;color:var(--ink-2);
  text-decoration:none;position:relative}
.stn:hover{color:var(--ink);background:color-mix(in srgb,var(--brass) 7%,transparent)}
.stn-n{position:relative;z-index:1;flex:none;width:20px;height:20px;border-radius:50%;display:grid;place-items:center;
  background:var(--page);border:2.5px solid var(--line-main);font:700 .6rem/1 var(--font-data);color:var(--ink)}
.stn.on{color:var(--ink);font-weight:650;background:color-mix(in srgb,var(--brass) 11%,transparent)}
.stn.on .stn-n{background:var(--line-main);color:#fff;border-color:var(--line-main)}

/* ---------- page header: the station sign ---------- */
.page-head{margin:0 0 1.8rem;padding:0 0 1.5rem;border-bottom:1px solid var(--border);position:relative}
.crumbs{font-family:var(--font-data);font-size:.68rem;text-transform:uppercase;letter-spacing:.09em;color:var(--muted);
  display:flex;gap:.55rem;align-items:center;margin-bottom:1.3rem}
.crumbs a{color:var(--muted);text-decoration:none}
.crumbs a:hover{color:var(--brass)}
.kicker{display:flex;align-items:center;gap:.65rem;font-family:var(--font-data);font-size:.72rem;font-weight:600;
  text-transform:uppercase;letter-spacing:.1em;color:var(--accent)}
.roundel{flex:none;width:34px;height:34px;border-radius:50%;display:grid;place-items:center;border:4px solid var(--accent);
  background:var(--surface);color:var(--ink);font:800 .9rem/1 var(--font-sign);letter-spacing:0}
.roundel-dot::after{content:"";width:9px;height:9px;border-radius:50%;background:var(--accent)}
.page-head h1{font-family:var(--font-sign);font-weight:800;font-size:clamp(2.1rem,4.6vw,3.15rem);line-height:1.04;
  letter-spacing:-.028em;text-wrap:balance;margin:.7rem 0 .9rem}
.lede{font-family:var(--font-read);font-style:italic;font-size:clamp(1.12rem,2.1vw,1.3rem);line-height:1.55;
  color:var(--ink-2);margin:0 0 1.1rem;max-width:38em;text-wrap:pretty}
.page-meta{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:.45rem .5rem;font-family:var(--font-sign);
  font-size:.78rem;color:var(--ink-2)}
.page-meta li{display:inline-flex;align-items:center;gap:.4rem;background:var(--surface);border:1px solid var(--border);
  border-radius:999px;padding:.28rem .7rem}
.page-meta code{background:none;padding:0;font-size:.74rem;color:var(--ink)}
.mk{font-family:var(--font-data);font-size:.6rem;text-transform:uppercase;letter-spacing:.09em;color:var(--muted)}
.mlink{color:var(--accent);font-weight:650;text-decoration:none}
.mlink:hover{text-decoration:underline}

/* ---------- content typography ---------- */
.content h2{font-family:var(--font-sign);font-weight:800;font-size:1.55rem;line-height:1.2;letter-spacing:-.015em;
  margin:2.9rem 0 .9rem;text-wrap:balance;position:relative}
.content h2::before{content:"";display:block;width:2.4rem;height:5px;border-radius:3px;background:var(--accent);margin-bottom:.85rem}
.content h3{font-family:var(--font-sign);font-weight:720;font-size:1.14rem;line-height:1.3;margin:2rem 0 .55rem;text-wrap:balance}
.content h4{font-family:var(--font-sign);font-size:1rem;margin:1.5rem 0 .4rem}
.h-anchor{margin-left:.45rem;color:var(--muted);text-decoration:none;font-weight:400;opacity:0;transition:opacity .15s}
h2:hover .h-anchor,h3:hover .h-anchor,.h-anchor:focus-visible{opacity:1}
.content p{margin:0 0 1.05rem;text-wrap:pretty;hanging-punctuation:first}
.content strong{font-weight:700}
.content ul,.content ol{margin:0 0 1.1rem;padding-left:1.35rem}
.content li{margin:.38rem 0}
.content li::marker{color:var(--muted)}
.content hr{border:none;height:1px;background:var(--border);margin:2.4rem 0}
.content blockquote{margin:1.3rem 0;padding:.85rem 1.15rem;border-left:4px solid var(--accent);
  background:color-mix(in srgb,var(--accent) 6%,var(--surface));border-radius:0 8px 8px 0;color:var(--ink);font-style:italic}
.content blockquote p:last-child{margin-bottom:0}
.content details{margin:.5rem 0 .6rem;padding:.35rem .8rem;background:var(--surface);border:1px solid var(--border);border-radius:8px}
.content details[open]{padding-bottom:.6rem}
.content summary{cursor:pointer;font-family:var(--font-sign);font-size:.8rem;font-weight:650;color:var(--link);
  list-style:none;display:flex;align-items:center;gap:.4rem}
.content summary::-webkit-details-marker{display:none}
.content summary::before{content:"+";display:inline-grid;place-items:center;width:1.05rem;height:1.05rem;border-radius:50%;
  border:1.5px solid currentColor;font:700 .72rem/1 var(--font-data)}
.content details[open] > summary::before{content:"−"}
.content .intro > p:first-child{font-size:1.04em}

/* ---------- math displays, formulas, code, terminals ---------- */
.math-display{font-family:var(--font-read);font-size:1.12rem;line-height:1.5;white-space:pre;text-align:center;
  overflow-x:auto;padding:.85rem 1rem;margin:1.2rem 0;border-radius:8px;
  background:linear-gradient(90deg,transparent,color-mix(in srgb,var(--accent) 7%,transparent),transparent);
  font-variant-numeric:lining-nums tabular-nums}
pre.formula{width:fit-content;max-width:100%;margin:1.3rem auto;background:var(--surface-2);border:none;
  border-left:3px solid color-mix(in srgb,var(--accent) 55%,transparent);border-radius:0 8px 8px 0}
pre.formula{font-size:.86rem;line-height:1.7}
.codewrap{position:relative}
.codewrap .copy-btn{position:absolute;top:.45rem;right:.45rem;font-family:var(--font-data);font-size:.6rem;
  text-transform:uppercase;letter-spacing:.06em;background:var(--surface);color:var(--ink-2);
  border:1px solid var(--border);border-radius:5px;padding:.28rem .55rem;cursor:pointer;opacity:0;transition:opacity .15s}
.codewrap:hover .copy-btn,.codewrap .copy-btn:focus-visible{opacity:1}
.codewrap .copy-btn:hover{border-color:var(--brass);color:var(--brass)}
.terminal{margin:1.3rem 0;border-radius:10px;overflow:hidden;background:var(--term-bg);
  border:1px solid color-mix(in srgb,#000 30%,var(--border));box-shadow:var(--shadow)}
.term-bar{display:flex;align-items:center;gap:6px;padding:.5rem .8rem;background:var(--term-bar);
  border-bottom:1px solid rgba(255,255,255,.06)}
.term-bar i{width:10px;height:10px;border-radius:50%;background:#ff5f57}
.term-bar i:nth-child(2){background:#febc2e}
.term-bar i:nth-child(3){background:#28c840}
.term-bar span{margin-left:.6rem;font-family:var(--font-data);font-size:.66rem;letter-spacing:.06em;color:var(--term-dim)}
.terminal pre{margin:0;background:transparent;border:none;border-radius:0;color:var(--term-ink);padding:.9rem 1.05rem 1rem}
.terminal pre{font-size:.79rem;line-height:1.55}
.terminal pre code{color:var(--term-ink)}
.terminal .tp{color:#6fd49b;user-select:none}
.terminal .tc{color:var(--term-cmd);font-weight:600}
.terminal .tk{color:var(--term-dim);font-style:italic}
.terminal .copy-btn{background:rgba(255,255,255,.06);color:var(--term-dim);border-color:rgba(255,255,255,.12);top:.35rem}
.terminal .codewrap .copy-btn{opacity:.85}
.terminal .copy-btn:hover{color:var(--term-cmd);border-color:var(--term-cmd)}

/* ---------- callouts (GitHub alerts) ---------- */
.callout{--c:var(--s1);margin:1.4rem 0;padding:.9rem 1.1rem .75rem;border-radius:10px;
  border:1px solid color-mix(in srgb,var(--c) 30%,var(--border));
  background:color-mix(in srgb,var(--c) 7%,var(--surface))}
.callout-tip{--c:var(--s2)} .callout-key{--c:var(--s5)} .callout-warn{--c:var(--s3)} .callout-caution{--c:var(--s6)}
.callout-title{font-family:var(--font-data);font-size:.66rem!important;font-weight:700;text-transform:uppercase;
  letter-spacing:.12em;color:var(--c);margin:0 0 .35rem!important;display:flex;align-items:center;gap:.45rem}
.callout-title::before{content:"";width:8px;height:8px;border-radius:50%;background:var(--c)}
.callout > :last-child{margin-bottom:0}
.callout .terminal,.callout pre{margin:.7rem 0}

/* ---------- figures, diagrams, tables ---------- */
.content{counter-reset:fig}
figure.figure{margin:2rem 0;text-align:center;counter-increment:fig}
figure.figure svg{max-width:100%;height:auto;color:var(--ink)}
figure.figure figcaption{font-family:var(--font-sign);font-size:.84rem;line-height:1.5;color:var(--ink-2);
  margin:.7rem auto 0;max-width:40rem;text-wrap:pretty}
figure.figure figcaption::before{content:"Figure " counter(fig) "  ";font-family:var(--font-data);font-size:.68rem;
  font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin-right:.35rem}
.diagram{margin:2rem 0;text-align:center}
.diagram svg{max-width:100%;height:auto;color:var(--ink)}
.tablewrap{overflow-x:auto;margin:1.3rem 0;border:1px solid var(--border);border-radius:10px;background:var(--surface)}
table{border-collapse:collapse;width:100%;font-family:var(--font-sign);font-size:.84rem;line-height:1.45;
  font-variant-numeric:tabular-nums}
th,td{padding:.55rem .8rem;border-bottom:1px solid var(--border);vertical-align:top}
td:first-child{white-space:nowrap;font-family:var(--font-data);font-size:.8rem;color:var(--ink-2)}
tbody tr:last-child td{border-bottom:none}
tbody tr:nth-child(even){background:color-mix(in srgb,var(--ink) 2.5%,transparent)}
tbody tr:hover{background:color-mix(in srgb,var(--brass) 7%,transparent)}
th{color:var(--ink-2);text-transform:uppercase;letter-spacing:.05em;font-size:.64rem;background:var(--surface-2);position:sticky;top:0}

/* ---------- sections with personalities ---------- */
.content section.sec[data-sec="then-now-next"]{margin:2.6rem 0 0;padding:0 0 .4rem}
.tnn{display:inline-block;font-family:var(--font-data);font-size:.62rem;font-weight:700;text-transform:uppercase;
  letter-spacing:.12em;padding:.28rem .55rem;border-radius:999px;vertical-align:.2em;margin-right:.6rem;color:#fff}
.tnn-then{background:var(--line-heritage)} .tnn-now{background:var(--line-cross)} .tnn-next{background:var(--line-express)}
.tnn-sep{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.content section[data-sec="then-now-next"] h3{margin-top:2.2rem}
.content section[data-sec="exercises"] > ol{counter-reset:ex;list-style:none;padding-left:0}
.content section[data-sec="exercises"] > ol > li{counter-increment:ex;position:relative;padding:.85rem 1rem .75rem 3rem;
  margin:.7rem 0;background:var(--surface);border:1px solid var(--border);border-radius:10px}
.content section[data-sec="exercises"] > ol > li::before{content:counter(ex);position:absolute;left:.9rem;top:.85rem;
  width:1.45rem;height:1.45rem;border-radius:50%;display:grid;place-items:center;background:var(--accent);color:#fff;
  font:700 .7rem/1 var(--font-sign)}
.diff{display:inline-block;font-size:.72rem;letter-spacing:.08em;padding:.05rem .45rem;margin-right:.3rem;border-radius:999px;
  vertical-align:.1em;font-family:var(--font-sign);font-weight:700;
  color:var(--c);background:color-mix(in srgb,var(--c) 13%,transparent);--c:var(--s2)}
.diff-2{--c:var(--s3)} .diff-3{--c:var(--s6)}
.content section[data-sec="see-it-move"]{margin-top:2.6rem;padding:1.3rem 1.4rem .4rem;border-radius:12px;
  background:linear-gradient(135deg,color-mix(in srgb,var(--accent) 9%,var(--surface)),var(--surface));
  border:1px solid color-mix(in srgb,var(--accent) 22%,var(--border))}
.content section[data-sec="see-it-move"] h2{margin-top:0}
.content section[data-sec="further-reading"] ul{list-style:none;padding-left:0}
.content section[data-sec="further-reading"] li{padding-left:1.4rem;position:relative}
.content section[data-sec="further-reading"] li::before{content:"";position:absolute;left:.15rem;top:.62em;width:.55rem;height:.55rem;
  border-radius:50%;border:2px solid var(--accent)}

/* ---------- on this page ---------- */
.page-toc{font-family:var(--font-sign);font-size:.8rem;line-height:1.45}
.toc-title{font-family:var(--font-data);font-size:.62rem;text-transform:uppercase;letter-spacing:.13em;color:var(--muted);margin:0 0 .6rem}
.page-toc ol{list-style:none;margin:0;padding:0}
.page-toc > ol{border-left:2px solid var(--border)}
.page-toc li{margin:0}
.page-toc a{display:block;padding:.26rem 0 .26rem .85rem;margin-left:-2px;border-left:2px solid transparent;
  color:var(--ink-2);text-decoration:none}
.page-toc ol ol a{padding-left:1.65rem;font-size:.76rem;color:var(--muted)}
.page-toc a:hover{color:var(--ink)}
.page-toc a.active{color:var(--accent);border-left-color:var(--accent);font-weight:650}
.toc-inline{display:none;margin:0 0 1.6rem;background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:.6rem .9rem}
.toc-inline summary{cursor:pointer;font-family:var(--font-data);font-size:.66rem;text-transform:uppercase;letter-spacing:.12em;color:var(--muted)}
.toc-inline .toc-title{display:none}
.toc-inline .page-toc{margin-top:.6rem}
.az{display:flex;flex-wrap:wrap;gap:.3rem;margin:1rem 0 1.6rem}
.az a{font-family:var(--font-data);font-size:.74rem;font-weight:700;width:1.9rem;height:1.9rem;display:grid;place-items:center;
  border-radius:6px;border:1px solid var(--border);background:var(--surface);color:var(--ink);text-decoration:none}
.az a:hover{border-color:var(--accent);color:var(--accent)}

/* ---------- pager ---------- */
.pager{display:grid;grid-template-columns:1fr 1fr;gap:.9rem;margin:3.2rem 0 0}
.pager a{display:flex;flex-direction:column;gap:.25rem;padding:.95rem 1.1rem;border:1px solid var(--border);border-radius:12px;
  background:var(--surface);text-decoration:none;color:var(--ink);transition:border-color .15s,transform .15s}
.pager a:hover{border-color:var(--accent);transform:translateY(-1px)}
.pager-next{text-align:right;grid-column:2}
.pager-dir{font-family:var(--font-data);font-size:.62rem;text-transform:uppercase;letter-spacing:.12em;color:var(--muted)}
.pager-title{font-family:var(--font-sign);font-weight:700;font-size:.98rem}

/* ---------- landing ---------- */
.hero{padding:.6rem 0 1.4rem}
.hero-grid{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);gap:2rem;align-items:center}
.eyebrow{font-family:var(--font-data);text-transform:uppercase;letter-spacing:.12em;font-size:.7rem;color:var(--brass);font-weight:700}
.hero-title{font-family:var(--font-sign);font-weight:850;font-size:clamp(2.4rem,5.4vw,3.9rem);line-height:.98;
  letter-spacing:-.035em;margin:.6rem 0 1rem;text-wrap:balance}
.hero-title span{color:var(--brass)}
.tagline{font-family:var(--font-read);font-size:clamp(1.05rem,1.9vw,1.2rem);line-height:1.6;color:var(--ink-2);max-width:34em;margin:0}
.cta-row{display:flex;flex-wrap:wrap;gap:.7rem;margin:1.5rem 0 .4rem}
.cta{font-family:var(--font-sign);font-weight:650;font-size:.92rem;padding:.7rem 1.1rem;border:1px solid var(--border-2);
  border-radius:8px;color:var(--ink);background:var(--surface);text-decoration:none;transition:border-color .15s,transform .15s}
.cta:hover{border-color:var(--brass);color:var(--brass);transform:translateY(-1px)}
.cta.primary{background:var(--brass);color:#fff;border-color:var(--brass)}
.cta.primary:hover{filter:brightness(1.07);color:#fff}
.hero-cf{margin:0;padding:1.3rem 1.2rem 1.1rem;border-radius:14px;border:1px solid var(--border);
  background:
    linear-gradient(var(--grid) 1px,transparent 1px) 0 0/100% 22px,
    linear-gradient(90deg,var(--grid) 1px,transparent 1px) 0 0/22px 100%,
    var(--surface);
  box-shadow:var(--shadow);text-align:center}
.cf{display:inline-flex;align-items:center;font-family:var(--font-read);font-size:clamp(1.25rem,2.4vw,1.6rem);
  color:var(--ink);line-height:1;padding:.4rem 0 .6rem}
.cf-lhs{color:var(--brass);font-style:italic;margin-right:.35em;font-size:1.15em}
.cf-term{white-space:nowrap;padding-right:.18em}
.cf-frac{display:inline-flex;flex-direction:column;align-items:stretch;vertical-align:middle;font-size:.9em}
.cf-num{text-align:center;border-bottom:1.5px solid currentColor;padding:0 .25em .22em}
.cf-den{display:inline-flex;align-items:center;justify-content:flex-start;padding-top:.22em}
.cf-tail{color:var(--muted);padding-left:.1em}
.hero-cf figcaption{font-family:var(--font-sign);font-size:.8rem;line-height:1.5;color:var(--ink-2);margin-top:.5rem}
.hero-cf b{color:var(--ink)}
.stats{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:.6rem;margin:2rem 0 .4rem}
.stat{padding:.75rem .8rem;border-top:3px solid var(--brass);background:var(--surface);border-radius:0 0 8px 8px;
  font-family:var(--font-sign)}
.stat:nth-child(2){border-top-color:var(--line-express)} .stat:nth-child(3){border-top-color:var(--line-cross)}
.stat:nth-child(4){border-top-color:var(--line-branch)} .stat:nth-child(5){border-top-color:var(--line-heritage)}
.stat:nth-child(6){border-top-color:var(--line-ref)}
.stat b{display:block;font-size:1.55rem;font-weight:800;letter-spacing:-.02em;line-height:1.1}
.stat span{font-size:.72rem;color:var(--ink-2);line-height:1.3;display:block;margin-top:.15rem}
.band{margin:2.4rem 0 0}
.band > h2{margin-top:0}
.network svg{max-width:100%;height:auto}
.content figure.network{counter-increment:none}
.content figure.network figcaption::before{content:none}
.card-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:.7rem;margin:1.1rem 0 .6rem}
.card{display:flex;flex-direction:column;gap:.2rem;padding:.8rem .9rem .85rem;border:1px solid var(--border);border-radius:10px;
  background:var(--surface);color:var(--ink);text-decoration:none;position:relative;overflow:hidden;
  transition:border-color .15s,transform .15s,box-shadow .15s}
.card::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--accent);opacity:.9}
.card:hover{border-color:color-mix(in srgb,var(--accent) 60%,var(--border));transform:translateY(-2px);box-shadow:var(--shadow)}
.card-num{font-family:var(--font-data);font-size:.68rem;font-weight:700;color:var(--accent);letter-spacing:.04em}
.card.stop .card-num{width:1.55rem;height:1.55rem;border-radius:50%;border:3px solid var(--line-main);display:grid;place-items:center;
  color:var(--ink);font-size:.62rem;margin-bottom:.2rem}
.card-title{font-family:var(--font-sign);font-weight:700;font-size:.93rem;line-height:1.3}
.card-note{font-size:.8rem;line-height:1.45;color:var(--ink-2)}
.card.express{--accent:var(--line-express)} .card.heritage{--accent:var(--line-heritage)} .card.branch{--accent:var(--line-branch)}
.teasers{grid-template-columns:repeat(auto-fill,minmax(205px,1fr))}
.card.teaser{--accent:var(--line-cross);padding-top:.9rem}
.card.teaser .card-title{font-size:.98rem}
.duo{display:grid;grid-template-columns:1fr 1fr;gap:.9rem}
.panel{display:flex;flex-direction:column;gap:.45rem;padding:1.2rem 1.25rem;border-radius:14px;text-decoration:none;color:var(--ink);
  border:1px solid color-mix(in srgb,var(--accent) 28%,var(--border));
  background:linear-gradient(160deg,color-mix(in srgb,var(--accent) 11%,var(--surface)),var(--surface) 70%);
  transition:transform .15s,box-shadow .15s}
.panel:hover{transform:translateY(-2px);box-shadow:var(--shadow)}
.panel-kicker{font-family:var(--font-data);font-size:.64rem;text-transform:uppercase;letter-spacing:.12em;color:var(--accent);font-weight:700}
.panel-title{font-family:var(--font-sign);font-size:1.25rem;font-weight:800;letter-spacing:-.01em}
.panel-body{font-size:.9rem;line-height:1.6;color:var(--ink-2)}
.panel-go{font-family:var(--font-sign);font-weight:700;font-size:.85rem;color:var(--accent);margin-top:auto}
.content .ref-list{list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:.5rem 1.4rem}
.content .page-meta,.content .page-toc ol{padding-left:0}
.content .page-meta{margin:0}
.content .page-toc li{margin:0}
body[data-page="index"] .layout{max-width:1340px}
body[data-page="index"] .content{max-width:62rem}

/* ---------- footer ---------- */
.site-footer{border-top:1px solid var(--border);margin-top:3rem;background:var(--surface)}
.foot-inner{max-width:1180px;margin:0 auto;padding:2rem clamp(1rem,4vw,3rem) 2.4rem;display:grid;
  grid-template-columns:minmax(0,1.6fr) repeat(3,minmax(0,1fr));gap:1.6rem;font-family:var(--font-sign);font-size:.82rem}
.foot-brand p{color:var(--ink-2);line-height:1.6;margin:.7rem 0 0;max-width:30rem}
.foot-col{display:flex;flex-direction:column;gap:.4rem;color:var(--ink-2)}
.foot-col a{color:var(--ink-2);text-decoration:none}
.foot-col a:hover{color:var(--brass)}
.foot-h{font-family:var(--font-data);font-size:.62rem;text-transform:uppercase;letter-spacing:.13em;color:var(--muted);margin-bottom:.2rem}

/* ---------- responsive ---------- */
@media (max-width:1240px){
  .layout.has-rail{grid-template-columns:260px minmax(0,1fr);max-width:1180px}
  .toc-rail{display:none}
  .toc-inline{display:block}
}
@media (max-width:980px){
  .hero-grid{grid-template-columns:1fr}
  .stats{grid-template-columns:repeat(3,minmax(0,1fr))}
  .foot-inner{grid-template-columns:1fr 1fr}
}
@media (max-width:860px){
  :root{--top:50px}
  body{font-size:16.5px}
  .layout,.layout.has-rail{grid-template-columns:1fr}
  .menu-btn{display:inline-flex}
  .sidebar{position:fixed;top:var(--top);left:0;bottom:0;width:290px;max-height:none;background:var(--page);z-index:35;
    transform:translateX(-105%);transition:transform .2s;border-right:1px solid var(--border);box-shadow:var(--shadow)}
  body.nav-open .sidebar{transform:none}
  .content{padding-top:1.4rem}
  .search{flex:1 1 120px}
  .top-link,.wordmark span{display:none}
  .duo{grid-template-columns:1fr}
  .pager{grid-template-columns:1fr}
  .pager-next{grid-column:1}
}
@media (max-width:520px){
  .stats{grid-template-columns:repeat(2,minmax(0,1fr))}
  .foot-inner{grid-template-columns:1fr}
  .content section[data-sec="exercises"] > ol > li{padding-left:2.6rem}
  .cf{font-size:1.05rem}
}
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  .card:hover,.cta:hover,.pager a:hover,.panel:hover{transform:none}
  .sidebar,.codewrap .copy-btn,.progress i{transition:none}
}

/* ---------- print ---------- */
@media print{
  :root,:root[data-theme="dark"],:root[data-theme="light"]{
    --page:#fff; --surface:#fff; --surface-2:#f6f6f6; --ink:#000; --ink-2:#333;
    --muted:#555; --grid:#ddd; --border:rgba(0,0,0,.25); --brass:#8a5a10; --link:#000;
    --term-bg:#fff; --term-bar:#fff; --term-ink:#000; --term-dim:#555; --term-cmd:#000;
  }
  .topbar,.sidebar,.site-footer,.skip-link,.toc-rail,.toc-inline,.search,.codewrap .copy-btn,.progress,.pager,.h-anchor,.term-bar{display:none!important}
  body{background:#fff;color:#000}
  .layout,.layout.has-rail{display:block;max-width:none}
  .content{max-width:none;padding:0}
  .terminal{box-shadow:none;border-color:#999}
  code{background:none}
  pre{background:#fff;border-color:#999}
  pre,blockquote,.tablewrap,tr,.diagram,figure.figure,.callout,.terminal,.math-display{page-break-inside:avoid}
  h1,h2,h3,h4{page-break-after:avoid}
}
"""

JS = r"""(function(){
  'use strict';
  var root=document.documentElement;

  // ---- theme: auto -> light -> dark ----
  var order=['auto','light','dark'];
  var labels={auto:'Auto',light:'Light',dark:'Dark'};
  var btn=document.getElementById('theme-toggle');
  function cur(){try{return localStorage.getItem('rct-theme')||'auto';}catch(e){return 'auto';}}
  function apply(m){
    root.setAttribute('data-theme',m);
    if(!btn)return;
    btn.setAttribute('data-mode',m);
    var t=btn.querySelector('.tt-label'); if(t)t.textContent=labels[m];
    btn.setAttribute('aria-label','Color theme: '+labels[m]+'. Click to change.');
  }
  apply(cur());
  if(btn)btn.addEventListener('click',function(){
    var m=order[(order.indexOf(cur())+1)%3];
    try{localStorage.setItem('rct-theme',m);}catch(e){}
    apply(m);
  });

  // ---- mobile navigation ----
  var menu=document.querySelector('.menu-btn');
  function setNav(open){
    document.body.classList.toggle('nav-open',open);
    if(menu)menu.setAttribute('aria-expanded',open?'true':'false');
  }
  if(menu)menu.addEventListener('click',function(){setNav(!document.body.classList.contains('nav-open'));});
  document.querySelectorAll('.sidebar a').forEach(function(a){
    a.addEventListener('click',function(){setNav(false);});
  });
  document.addEventListener('keydown',function(e){if(e.key==='Escape')setNav(false);});
  // keep the current station in view inside a long sidebar
  var on=document.querySelector('.sidebar .on');
  if(on&&on.scrollIntoView){try{on.scrollIntoView({block:'nearest'});}catch(e){}}
})();

// ---- copy buttons (terminals copy their commands, without prompts) ----
(function(){
  document.querySelectorAll('.content pre').forEach(function(pre){
    var wrap=document.createElement('div');
    wrap.className='codewrap';
    pre.parentNode.insertBefore(wrap,pre);
    wrap.appendChild(pre);
    var btn=document.createElement('button');
    btn.type='button';btn.className='copy-btn';btn.textContent='Copy';
    btn.addEventListener('click',function(){
      var text;
      var cmds=pre.querySelectorAll('.tc');
      if(cmds.length){text=Array.prototype.map.call(cmds,function(c){return c.textContent;}).join('\n');}
      else{text=(pre.querySelector('code')||pre).textContent;}
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

// ---- reading progress + "on this page" scrollspy ----
(function(){
  var bar=document.querySelector('.progress i');
  var links=document.querySelectorAll('.toc-rail a[href^="#"]');
  var byId={};
  Array.prototype.forEach.call(links,function(a){byId[decodeURIComponent(a.getAttribute('href').slice(1))]=a;});
  var heads=Array.prototype.filter.call(document.querySelectorAll('.content h2[id], .content h3[id]'),function(h){return byId[h.id];});
  var active=null, ticking=false;
  function update(){
    ticking=false;
    var doc=document.documentElement;
    var max=doc.scrollHeight-window.innerHeight;
    if(bar)bar.style.width=(max>0?Math.min(100,Math.max(0,window.scrollY/max*100)):0)+'%';
    if(!heads.length)return;
    var y=window.scrollY+110, cur=null;
    for(var i=0;i<heads.length;i++){ if(heads[i].getBoundingClientRect().top+window.scrollY<=y)cur=heads[i]; else break; }
    var link=cur?byId[cur.id]:null;
    if(link!==active){
      if(active)active.classList.remove('active');
      active=link;
      if(active){active.classList.add('active');
        var rail=document.querySelector('.toc-rail');
        if(rail){var r=active.getBoundingClientRect(),rr=rail.getBoundingClientRect();
          if(r.top<rr.top||r.bottom>rr.bottom)rail.scrollTop+=r.top-rr.top-rr.height/3;}}
    }
  }
  window.addEventListener('scroll',function(){if(!ticking){ticking=true;window.requestAnimationFrame(update);}},{passive:true});
  window.addEventListener('resize',update);
  update();
})();

// ---- client-side search over the build-time index (assets/search-index.js) ----
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
    var scored=[];
    for(var p=0;p<idx.length;p++){
      var pg=idx[p];
      for(var h=0;h<pg.h.length;h++){
        var sec=pg.h[h];
        var head=sec.t.toLowerCase();
        var hay=(pg.t+' '+sec.t+' '+sec.s).toLowerCase();
        if(!terms.every(function(t){return hay.indexOf(t)>=0;}))continue;
        var score=terms.reduce(function(s,t){return s+(head.indexOf(t)>=0?2:0);},0);
        scored.push({score:score,order:scored.length,href:pg.p+'#'+sec.id,page:pg.t,head:sec.t,snip:sec.s});
      }
    }
    scored.sort(function(a,b){return b.score-a.score||a.order-b.order;});
    hits=scored.slice(0,14);
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
  // "/" (or Ctrl/Cmd-K) jumps to search from anywhere that is not a text field
  document.addEventListener('keydown',function(e){
    var t=e.target, typing=t&&(t.tagName==='INPUT'||t.tagName==='TEXTAREA'||t.isContentEditable);
    if((e.key==='/'&&!typing)||((e.ctrlKey||e.metaKey)&&(e.key==='k'||e.key==='K'))){
      e.preventDefault();input.focus();input.select();
    }
  });
})();
"""


if __name__ == "__main__":
    build()
    print("Site built under docs/. Enable GitHub Pages -> Deploy from branch -> /docs.")
