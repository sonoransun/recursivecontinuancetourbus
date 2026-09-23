"""Markdown-converter tests for build_site.py: figures, mermaid, landing data.

Covers the block-image -> inline-``<figure>`` rule, the loud failures for
unknown assets and inline image syntax, mermaid fence dispatch, the link
rewrite regression, search-snippet exclusions, and the Express/Heritage
landing-section parsers.
"""

from __future__ import annotations

import pytest


@pytest.fixture(scope="module")
def site(load_module):
    return load_module("build_site")


# --- block images -> inline <figure> ---------------------------------------- #

TINY_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
    '<circle cx="5" cy="5" r="4" fill="currentColor"/></svg>'
)


def _asset(tmp_path, name="fig-test.svg", body=TINY_SVG):
    assets = tmp_path / "assets"
    assets.mkdir(exist_ok=True)
    (assets / name).write_text(body)
    return f"assets/{name}"


def test_block_image_inlines_svg_and_escapes_caption(site, tmp_path):
    src = _asset(tmp_path)
    out = site._figure_html("a <caption> & more", src, "doc.md", 7, base=tmp_path)
    assert out.startswith('<figure class="figure"><svg ')
    assert TINY_SVG in out  # the SVG document itself, not an <img>
    assert "<img" not in out
    assert "<figcaption>a &lt;caption&gt; &amp; more</figcaption>" in out
    assert out.endswith("</figure>")


def test_figure_caption_supports_inline_markdown(site, tmp_path):
    src = _asset(tmp_path)
    out = site._figure_html("The **butterfly** at `q<=20`", src, "doc.md", 1, base=tmp_path)
    assert "<figcaption>The <strong>butterfly</strong> at <code>q&lt;=20</code></figcaption>" in out


def test_unknown_figure_asset_dies_with_file_and_line(site):
    md = "intro\n\n![cap](assets/fig-does-not-exist.svg)\n"
    with pytest.raises(SystemExit) as excinfo:
        site.md_to_html(md, src_name="doc.md")
    assert str(excinfo.value).startswith(
        "doc.md:3: unknown figure asset 'assets/fig-does-not-exist.svg'"
    )


@pytest.mark.parametrize(
    "src",
    [
        "assets/other.svg",  # exists below, but off the fig- prefix
        "assets/fig-test.png",  # wrong extension
        "fig-test.svg",  # not under assets/
    ],
)
def test_offprefix_asset_paths_die_even_if_present(site, tmp_path, src):
    _asset(tmp_path, "fig-test.svg")
    _asset(tmp_path, "other.svg")
    _asset(tmp_path, "fig-test.png")
    (tmp_path / "fig-test.svg").write_text(TINY_SVG)
    with pytest.raises(SystemExit) as excinfo:
        site._figure_html("cap", src, "doc.md", 4, base=tmp_path)
    assert str(excinfo.value).startswith(f"doc.md:4: unknown figure asset {src!r}")


def test_inline_image_in_paragraph_dies(site):
    md = "words before ![cap](assets/fig-a.svg) words after"
    with pytest.raises(SystemExit) as excinfo:
        site.md_to_html(md, src_name="doc.md")
    assert (
        str(excinfo.value)
        == "doc.md: inline image syntax is not supported; put ![...](...) on its own line"
    )


def test_figure_line_splits_adjacent_paragraph(site, monkeypatch):
    calls = []

    def stub(caption, src, src_name, line_no, base=None):
        calls.append((caption, src, src_name, line_no))
        return "<figure-stub/>"

    monkeypatch.setattr(site, "_figure_html", stub)
    out = site.md_to_html("before\n![cap](assets/fig-a.svg)\nafter", src_name="doc.md")
    assert "<p>before</p>" in out
    assert "<p>after</p>" in out
    assert "<figure-stub/>" in out
    assert out.index("<p>before</p>") < out.index("<figure-stub/>") < out.index("<p>after</p>")
    assert calls == [("cap", "assets/fig-a.svg", "doc.md", 2)]


def test_para_breaks_on_figure_lines(site):
    assert site._para_breaks("![cap](assets/fig-a.svg)")
    assert not site._para_breaks("plain prose line")


# --- link rewrite regression ------------------------------------------------- #

def test_md_links_still_rewrite_to_html(site):
    out = site.md_to_html("See [a](b.md) for more.", src_name="doc.md")
    assert '<a href="b.html">a</a>' in out


# --- mermaid fences ---------------------------------------------------------- #

def test_mermaid_fence_dispatches_to_the_renderer(site):
    md = "intro\n\n```mermaid\nflowchart TD\nA[one] --> B[two]\n```\n"
    out = site.md_to_html(md, src_name="doc.md")
    assert '<figure class="diagram"' in out
    assert "<svg" in out
    assert ">one</text>" in out and ">two</text>" in out
    assert "<pre" not in out  # never a code block, so no copy button
    assert "lang-mermaid" not in out


def test_mermaid_fence_errors_point_into_the_md_file(site):
    md = "a\nb\n\n```mermaid\nflowchart TD\nA --> B & C\n```\n"
    with pytest.raises(site.MermaidError) as excinfo:
        site.md_to_html(md, src_name="doc.md")
    # opening fence on line 4; the offending '&' fan-out sits on line 6
    assert str(excinfo.value).startswith("doc.md:6: ")


def test_python_fence_still_emits_pre_code(site):
    out = site.md_to_html("```python\nprint('hi')\n```\n", src_name="doc.md")
    assert '<pre><code class="lang-python">' in out
    assert "print(&#x27;hi&#x27;)" in out
    assert "<figure" not in out


# --- search snippets --------------------------------------------------------- #

def test_snippets_skip_fence_bodies_and_figure_lines(site):
    text = (
        "# Title\n"
        "Intro sentence.\n"
        "```mermaid\n"
        "flowchart TD\n"
        "Zebra --> Yak\n"
        "```\n"
        "![Figure caption here](assets/fig-x.svg)\n"
        "Tail sentence.\n"
    )
    secs = site._headings_with_snippets(text)
    assert [s["t"] for s in secs] == ["Title"]
    snippet = secs[0]["s"]
    assert "Zebra" not in snippet and "flowchart" not in snippet
    assert "Figure caption" not in snippet
    assert snippet == "Intro sentence. Tail sentence."


# --- landing-section parsers ------------------------------------------------- #

def test_express_sections_shape_on_synthetic_markdown(site, tmp_path):
    md = tmp_path / "d.md"
    md.write_text(
        "# Appendix D\n\n"
        "## E1 — The Markov Spectrum: the numbers after phi\n\nbody\n\n"
        "## Interlude\n\n"
        "## E2 — Continuants\n"
    )
    secs = site._express_sections(md)
    assert [(label, rest) for label, _anchor, rest in secs] == [
        ("E1", "The Markov Spectrum: the numbers after phi"),
        ("E2", "Continuants"),
    ]
    assert secs[0][1] == "e1-the-markov-spectrum-the-numbers-after-phi"
    assert secs[1][1] == site._slug("E2 — Continuants")


def test_heritage_sections_shape_on_synthetic_markdown(site, tmp_path):
    md = tmp_path / "h.md"
    md.write_text(
        "# Appendix H — The Heritage Line\n\n"
        "## The route through time\n\n"
        "## H1 — The Ladder of Euclid (c. 300 BC)\n\nbody\n\n"
        "## Interlude — The classical century\n\n"
        "## H2 — The Cyclic Method\n\n"
        "## How it ends\n\n"
        "## H6 — Item 101 (1972)\n"
    )
    secs = site._heritage_sections(md)
    assert [(label, rest) for label, _anchor, rest in secs] == [
        ("H1", "The Ladder of Euclid (c. 300 BC)"),
        ("H2", "The Cyclic Method"),
        ("H6", "Item 101 (1972)"),
    ]
    assert secs[0][1] == site._slug("H1 — The Ladder of Euclid (c. 300 BC)")


def test_heritage_sections_missing_file_is_empty(site, tmp_path):
    assert site._heritage_sections(tmp_path / "absent.md") == []


def test_curated_heritage_blurbs_shape(site):
    assert len(site.HERITAGE) == 9
    for title, blurb in site.HERITAGE:
        assert isinstance(title, str) and title
        assert isinstance(blurb, str) and blurb


def test_curated_branch_blurbs_shape(site):
    assert len(site.BRANCH) == 6
    for title, blurb in site.BRANCH:
        assert isinstance(title, str) and title
        assert isinstance(blurb, str) and blurb


def test_branch_sections_shape_on_synthetic_markdown(site, tmp_path):
    md = tmp_path / "i.md"
    md.write_text(
        "# Appendix I — The Branch Line\n\n"
        "## B1 — Engel Expansions: the ascending staircase\n\nbody\n\n"
        "## B2 — Lüroth and Pierce: the honest casino\n\n"
        "## Not a stop\n\n"
        "## B6 — Lochs' Theorem: the exchange rate\n"
    )
    secs = site._branch_sections(md)
    assert [(label, rest) for label, _anchor, rest in secs] == [
        ("B1", "Engel Expansions: the ascending staircase"),
        ("B2", "Lüroth and Pierce: the honest casino"),
        ("B6", "Lochs' Theorem: the exchange rate"),
    ]
    assert secs[0][1] == site._slug("B1 — Engel Expansions: the ascending staircase")


# --- nav + reference wiring -------------------------------------------------- #

def test_nav_heritage_group_sits_between_crossdomain_and_reference(site):
    nav = site.nav_html("index")
    i_cd = nav.index(">Cross-Domain<")
    i_h = nav.index(">Heritage<")
    i_branch = nav.index(">Branch<")
    i_ref = nav.index(">Reference<")
    assert i_cd < i_h < i_branch < i_ref
    assert 'href="appendix-h-history.html"' in nav
    assert 'href="appendix-i-branches.html"' in nav
    assert "A History in Convergents" in nav


def test_syllabus_is_the_last_reference_entry_and_in_nav(site):
    assert site.REFERENCE[-1] == ("syllabus", "Syllabus — for instructors")
    nav = site.nav_html("syllabus")
    assert '<a class="on" href="syllabus.html">Syllabus — for instructors</a>' in nav


# --- fences by kind: terminal, display, formula ------------------------------ #

def test_transcript_fence_becomes_a_terminal(site):
    out = site.md_to_html("```\n$ python -m tourbus demo pell 2\nx = 3\n```\n")
    assert '<div class="terminal">' in out
    assert '<span class="tp">$</span> <span class="tc">python -m tourbus demo pell 2</span>' in out
    assert "\nx = 3</code></pre></div>" in out


def test_bare_command_fence_gets_prompts_and_dim_comments(site):
    out = site.md_to_html("```\npython -m tourbus branch   # the Branch Line\n```\n")
    assert '<span class="tc">python -m tourbus branch</span>' in out
    assert '<span class="tk"># the Branch Line</span>' in out


def test_single_line_fence_is_a_math_display(site):
    out = site.md_to_html("```\nx² − d·y² = 1 < 2\n```\n")
    assert out == '<div class="math-display">x² − d·y² = 1 &lt; 2</div>'


def test_multi_line_fence_is_an_aligned_formula(site):
    out = site.md_to_html("```\na = 1\nbb = 22\n```\n")
    assert out == '<pre class="formula"><code>a = 1\nbb = 22</code></pre>'


# --- GitHub alerts -> callouts ----------------------------------------------- #

def test_github_alert_becomes_a_callout(site):
    md = "> [!TIP]\n> Run **this**:\n>\n> - one\n> - two\n"
    out = site.md_to_html(md)
    assert out.startswith('<aside class="callout callout-tip" role="note">')
    assert '<p class="callout-title">Try it</p>' in out
    assert "<p>Run <strong>this</strong>:</p>" in out
    assert "<ul><li>one</li><li>two</li></ul>" in out


def test_plain_blockquote_is_unchanged(site):
    assert site.md_to_html("> a *quote*\n> continues\n") == \
        "<blockquote>a <em>quote</em> continues</blockquote>"


# --- loose numbered lists ---------------------------------------------------- #

def test_blank_lines_between_numbered_items_keep_one_list(site):
    md = "1. first\n   <details><summary>Hint</summary>h</details>\n\n2. second\n\n3. third\n"
    out = site.md_to_html(md)
    assert out.count("<ol>") == 1 and out.count("<li>") == 3


def test_a_restarted_list_is_a_new_list(site):
    out = site.md_to_html("1. a\n\n1. b\n")
    assert out.count("<ol>") == 2


# --- page assembly ------------------------------------------------------------ #

def test_stop_page_gets_station_sign_rail_and_pager(site):
    md = (
        "[Route map](index.md) · [Next →](02-unfolding-road.md)\n\n"
        "# Stop 1 — The Depot\n\n> An epigraph.\n\n## Overview\n\ntext\n\n"
        "## Then, now, next\n\n### Then — old\n\nx\n\n### Now — new\n\ny\n\n"
        "## Exercises\n\n1. **(★★)** go\n"
    )
    content, rail, desc, title = site.page_content("01-depot", md, "01-depot.md")
    assert '<h1 id="stop-1-the-depot">The Depot</h1>' in content
    assert "Main line · Stop 1 of 15" in content
    assert '<p class="lede">An epigraph.</p>' in content
    assert "chapter-nav" not in content          # the Markdown nav strip is replaced...
    assert 'class="pager-next" href="02-unfolding-road.html"' in content  # ...by a pager
    assert '<section class="sec" data-sec="then-now-next">' in content
    assert '<span class="tnn tnn-then">Then</span>' in content
    assert 'class="diff diff-2"' in content
    assert 'href="#then-now-next"' in rail and 'href="#then-old"' in rail
    assert desc == "An epigraph."
    assert title == "The Depot — Stop 1 · Tour Bus"


def test_every_anchor_into_the_exposition_exists(site):
    """Search hits and "Live widget" chips must land on real section ids."""
    import re
    from pathlib import Path

    expo = (Path(site.__file__).parent / "site" / "index.html").read_text()
    ids = set(re.findall(r'<section id="([^"]+)"', expo))
    wanted = [sid for sid, _t, _s in site.EXPLORE_SECTIONS]
    wanted += site.STOP_EXPLORE + list(site.LINE_EXPLORE.values())
    missing = [w for w in wanted if w not in ids]
    assert not missing, missing
    assert len(site.STOP_EXPLORE) == len(site.STOPS) == len(site.STOP_BLURBS)


def test_difficulty_badges_leave_code_alone(site):
    out = site._difficulty_badges("<p>(★)</p><pre><code>(★)</code></pre>")
    assert out.startswith('<p><span class="diff diff-1"')
    assert out.endswith("<pre><code>(★)</code></pre>")


# --- content contract: every stop keeps its "Then, now, next" ---------------- #

def test_every_stop_has_then_now_next_with_a_timeline(site):
    """Each chapter closes its lesson with history (a mermaid timeline), today's
    applications, and the open road — in that order, before the exercises."""
    import re
    from pathlib import Path

    docs = Path(site.__file__).parent / "docs"
    for slug, _title in site.STOPS:
        text = (docs / f"{slug}.md").read_text(encoding="utf-8")
        h2 = re.findall(r"^## (.+)$", text, flags=re.M)
        assert "Then, now, next" in h2, slug
        assert h2.index("Then, now, next") < h2.index("Exercises"), slug
        sec = text.split("## Then, now, next", 1)[1].split("\n## ", 1)[0]
        tags = re.findall(r"^### (Then|Now|Next) — ", sec, flags=re.M)
        assert tags == ["Then", "Now", "Next"], (slug, tags)
        assert "```mermaid\ntimeline" in sec, slug
