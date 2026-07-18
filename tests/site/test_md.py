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
    assert site.REFERENCE[-1] == ("syllabus", "Syllabus - for instructors")
    nav = site.nav_html("syllabus")
    assert '<a class="on" href="syllabus.html">Syllabus - for instructors</a>' in nav
