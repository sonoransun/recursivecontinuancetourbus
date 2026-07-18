"""Grammar, rejection, layout, and determinism tests for build_mermaid.py."""

from __future__ import annotations

import math
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

# --- the four real diagrams the renderer must handle ------------------------ #

TIMELINE_SRC = """\
timeline
    title Twenty-three centuries of continued fractions
    section Antiquity and India
        c. 300 BC : Euclid's Elements — the gcd ladder (VII.1-2) and the never-ending measuring test for incommensurables (X.2)
        499 : Aryabhata's kuttaka pulverizes linear indeterminate equations
        628 : Brahmagupta's bhavana composes solutions of x^2 - d y^2 = k
        1150 : Bhaskara II's chakravala dispatches d = 61
    section The Italian prelude
        1572 : Bombelli approximates sqrt(13) with an iterated fraction
        1613 : Cataldi gives the fraction its first notation, on sqrt(18)
        1655 : Brouncker finds 4/pi and Wallis records it in Arithmetica Infinitorum
        1695 : Wallis names the continued fraction
        1698 : Huygens' planetarium gears, chosen by convergents, appear in print
    section The classical century
        1737 : Euler founds the theory and unfolds e
        1761 : Lambert proves pi irrational through tan x
        1770 : Lagrange proves the periodicity of quadratic irrationals
    section The arithmetic and metric era
        1812 : Gauss states the invariant measure in a letter to Laplace
        1828 : Galois, at seventeen, characterizes the purely periodic expansions
        1844 : Lame counts Euclid's steps — the first complexity theorem
        1858-1861 : Stern the mathematician and Brocot the clockmaker grow the tree of fractions
        1879 : Markov charts the spectrum beyond the golden ratio
        1891 : Hurwitz sharpens approximation to within 1 over sqrt(5) q^2
        1913 : Perron's treatise appears and Ramanujan's letters reach Hardy
        1935 : Khinchin finds the constant hiding in almost every expansion
    section The computational era
        1972 : Gosper streams exact continued-fraction arithmetic in HAKMEM item 101
        1979 : Apery proves zeta(3) irrational with a runaway continued fraction
        1990 : Wiener breaks short-exponent RSA with convergents and Vuillemin formalizes exact real arithmetic
        2003 : Galperin's colliding blocks count the digits of pi
"""

SYLLABUS_SRC = """\
flowchart TD
    S1["1 The Depot"] --> S2["2 The Unfolding Road"]
    S2 --> S3["3 The Engine Room"]
    S3 --> S4["4 The Golden Milestone"]
    S3 --> S5["5 Scenic Overlook"]
    S4 --> S5
    S4 --> S6["6 The Loop Road"]
    S5 --> S6
    S6 --> S7["7 The Cattle Crossing"]
    S3 --> S8["8 The Family Tree"]
    S6 --> S8
    S2 --> S9["9 Celebrity Sightings"]
    S8 --> S9
    S9 --> S10["10 The Casino"]
    S6 --> S11["11 The Assembly Line"]
    S10 --> S11
    S11 --> S12["12 The Tower"]
    S6 --> S13["13 Hall of Mirrors"]
    S12 --> S13
    S5 --> S14["14 The Souvenir Shop"]
    S13 --> S14
    S14 --> S15["15 Terminus"]
    S15 -->|"past the terminus"| EX["Express Line E1-E7"]
    S3 -->|"the same recurrence"| CD["Cross-Domain C1-C7"]
    S1 -->|"the same road, in time"| HL["Heritage Line H1-H6"]
"""

GOSPER_SRC = """\
flowchart TD
    A["state (a, b, c, d)"] --> B["test: floor(a/c) = floor((a+b)/(c+d)) ?"]
    B -->|"yes - the next output digit is forced"| C["emit q = floor(a/c)"]
    C --> D["state becomes (c, d, a - q*c, b - q*d)"]
    D --> B
    B -->|"no - not yet certain"| E["ingest next input term p"]
    E --> F["state becomes (a*p + b, a, c*p + d, c)"]
    F --> B
"""

CHAKRAVALA_SRC = """\
flowchart TD
    A["trial triple (a, b, k) with a^2 - d b^2 = k"] --> B["choose m: b m = -a (mod |k|), m^2 as close to d as possible"]
    B --> C["compose with (m, 1, m^2 - d) by bhavana"]
    C --> D["divide by k: new triple (a', b', k')"]
    D --> E["is k' = 1 ?"]
    E -->|"no - turn the wheel again"| B
    E -->|"yes"| F["(a', b') solves x^2 - d y^2 = 1"]
"""

FIXTURES = [
    ("timeline", TIMELINE_SRC),
    ("syllabus", SYLLABUS_SRC),
    ("gosper", GOSPER_SRC),
    ("chakravala", CHAKRAVALA_SRC),
]


@pytest.fixture(scope="module")
def mermaid(load_module):
    return load_module("build_mermaid")


def _viewbox(svg: str) -> tuple[float, float]:
    m = re.search(r'viewBox="0 0 ([0-9.]+) ([0-9.]+)"', svg)
    assert m, "missing viewBox"
    return float(m.group(1)), float(m.group(2))


# --- grammar acceptance ----------------------------------------------------- #

def test_flowchart_shapes_chain_comments(mermaid):
    out = mermaid.render_diagram(
        "flowchart TD\n"
        "    %% a comment line\n"
        "    A[Start] --> B(Middle) --> C{Choice?}\n"
        "\n"
        "    C -->|yes| D[Done]\n"
        "    C -->|no| E[Retry]\n"
    )
    assert out.startswith('<figure class="diagram" role="figure"><svg ')
    assert out.endswith("</svg></figure>")
    assert 'role="img"' in out
    assert "<title>Start</title>" in out
    # 4 arrowheads plus the diamond body are the only polygons.
    assert out.count("<polygon") == 5
    assert 'rx="15"' in out  # the stadium
    assert "id=" not in out
    assert "<defs" not in out and "marker" not in out


def test_lr_is_the_transpose_of_td(mermaid):
    src = "flowchart {}\nA[one] --> B[two] --> C[three]\n"
    td_w, td_h = _viewbox(mermaid.render_diagram(src.format("TD")))
    lr_w, lr_h = _viewbox(mermaid.render_diagram(src.format("LR")))
    assert td_h > td_w
    assert lr_w > lr_h


def test_quoted_labels_allow_delimiters(mermaid):
    out = mermaid.render_diagram(
        'flowchart TD\n'
        '    A["choose m: (mod |k|)"] -->|"no - not yet certain"| B["x = y"]\n'
    )
    assert "choose m: (mod |k|)" in out
    assert "no - not yet certain" in out
    assert "x = y" in out


def test_bare_ids_and_unquoted_edge_label(mermaid):
    out = mermaid.render_diagram("flowchart TD\nA --> B\nA -->|maybe| C[c]\n")
    assert "<title>A</title>" in out  # bare first mention labels itself
    assert ">maybe</text>" in out


def test_label_text_is_escaped(mermaid):
    out = mermaid.render_diagram('flowchart TD\nA["a & b"] --> B[c]\n')
    assert "a &amp; b" in out


def test_timeline_with_title_sections_and_multi_event(mermaid):
    out = mermaid.render_diagram(
        "timeline\n"
        "    title Test line\n"
        "    section Alpha\n"
        "        1900 : first thing\n"
        "        1910 : second thing : third thing\n"
        "    section Beta\n"
        "        1920 : last thing\n"
    )
    assert out.startswith('<figure class="diagram" role="figure"><svg ')
    assert "<title>Test line</title>" in out
    assert out.count("<circle") == 3  # one dot per entry
    assert ">ALPHA</text>" in out and ">BETA</text>" in out
    assert "var(--brass,#b5751a)" in out
    assert "third thing" in out  # second event stacked under the same dot
    assert "id=" not in out


def test_timeline_without_title(mermaid):
    out = mermaid.render_diagram(
        "timeline\nsection Only\n1900 : a thing happened\n"
    )
    assert "<title>Only</title>" in out
    assert out.count("<circle") == 1


# --- rejection with src_name:line ------------------------------------------- #

REJECTS = [
    ("graph TD\n  A --> B", 1, "graph"),
    ("flowchart BT\n  A --> B", 1, "BT"),
    ("flowchart RL\n  A --> B", 1, "RL"),
    ("flowchart TD\n  A -.-> B", 2, "-.->"),
    ("flowchart TD\n  A ==> B", 2, "==>"),
    ("flowchart TD\n  A --- B", 2, "---"),
    ("flowchart TD\n  A --o B", 2, "--o"),
    ("flowchart TD\n  subgraph S\n  A --> B\n  end", 2, "subgraph"),
    ("flowchart TD\n  A[x]\n  style A fill:#fff", 3, "style"),
    ("flowchart TD\n  classDef k fill:#fff", 2, "classDef"),
    ("flowchart TD\n  linkStyle 0 stroke:red", 2, "linkStyle"),
    ("flowchart TD\n  click A callback", 2, "click"),
    ("flowchart TD\n  A --> B & C", 2, "&"),
    ("flowchart TD\n  A[has <br/> break]", 2, "HTML"),
    ("flowchart TD\n  A[a|b] --> C[c]", 2, "quote"),
    ("flowchart TD\n  ???", 2, "???"),
    ("timeline\n  section S\n  no colon here", 3, "period"),
]


@pytest.mark.parametrize(("source", "line", "needle"), REJECTS)
def test_rejections_carry_file_and_line(mermaid, source, line, needle):
    with pytest.raises(mermaid.MermaidError) as excinfo:
        mermaid.render_diagram(source, src_name="doc.md", line_no=0)
    message = str(excinfo.value)
    assert message.startswith(f"doc.md:{line}: ")
    assert needle in message


def test_line_numbers_are_offset_by_line_no(mermaid):
    src = "flowchart TD\n  A[ok]\n\n  %% fine\n  A --> B & C"
    with pytest.raises(mermaid.MermaidError) as excinfo:
        mermaid.render_diagram(src, src_name="doc.md", line_no=10)
    assert str(excinfo.value).startswith("doc.md:15: ")


def test_unlayerable_cycle_errors(mermaid):
    # Every node sits on a cycle: no in-degree-0 entry, nothing to layer from.
    with pytest.raises(mermaid.MermaidError) as excinfo:
        mermaid.render_diagram("flowchart TD\nA --> B\nB --> A",
                               src_name="doc.md", line_no=0)
    assert str(excinfo.value).startswith("doc.md:1: ")
    assert "layer" in str(excinfo.value)


# --- determinism and the four real fixtures --------------------------------- #

@pytest.mark.parametrize(("name", "source"), FIXTURES)
def test_fixture_renders_deterministically(mermaid, name, source):
    first = mermaid.render_diagram(source, src_name=f"{name}.md", line_no=3)
    second = mermaid.render_diagram(source, src_name=f"{name}.md", line_no=3)
    assert first == second
    assert first.startswith('<figure class="diagram" role="figure"><svg ')
    assert "id=" not in first
    assert "<defs" not in first and "marker" not in first


def test_gosper_loop_back_edges_and_arrowheads(mermaid):
    out = mermaid.render_diagram(GOSPER_SRC)
    # 7 edges, all-rectangle nodes: every polygon is an arrowhead.
    assert out.count("<polygon") == 7
    # Two back-edges (D --> B and F --> B) render as return polylines.
    assert out.count("<polyline") == 2
    assert "id=" not in out


def test_chakravala_wheel_back_edge_and_label(mermaid):
    out = mermaid.render_diagram(CHAKRAVALA_SRC)
    # 6 edges, all-rectangle nodes: every polygon is an arrowhead.
    assert out.count("<polygon") == 6
    # One back-edge (E --> B), its label riding the vertical lane segment.
    assert out.count("<polyline") == 1
    assert "no - turn the wheel again" in out
    assert "id=" not in out


# --- every real mermaid fence in docs/ must render -------------------------- #

def _mermaid_blocks(text: str) -> list[tuple[int, str]]:
    """(1-based fence line, body) for each ```mermaid fence in the text."""
    blocks = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            j = i + 1
            while j < len(lines) and lines[j].strip() != "```":
                j += 1
            if lang == "mermaid":
                blocks.append((i + 1, "\n".join(lines[i + 1:j])))
            i = j + 1
        else:
            i += 1
    return blocks


def test_all_docs_mermaid_blocks_render(mermaid):
    for path in sorted((ROOT / "docs").glob("*.md")):
        for fence_line, body in _mermaid_blocks(path.read_text(encoding="utf-8")):
            out = mermaid.render_diagram(body, src_name=path.name,
                                         line_no=fence_line)
            assert out.startswith('<figure class="diagram" role="figure">'), (
                f"{path.name}:{fence_line}")


# --- no edge segment may tunnel through a non-endpoint node box ------------- #

def _attrs(tag: str) -> dict[str, str]:
    return dict(re.findall(r'([\w-]+)="([^"]*)"', tag))


def _points(spec: str) -> list[tuple[float, float]]:
    return [tuple(map(float, p.split(","))) for p in spec.split()]


def _node_polys(svg: str) -> list[list[tuple[float, float]]]:
    """Convex outline of every node box (rect, stadium, or diamond).

    Node boxes carry ``stroke="currentColor"``; the surface-backed rects that
    sit under edge labels do not, so a stroke filter keeps labels out.
    """
    polys = []
    for tag in re.findall(r"<rect [^>]*/>", svg):
        a = _attrs(tag)
        if a.get("stroke") != "currentColor":
            continue
        x, y, w, h = (float(a["x"]), float(a["y"]),
                      float(a["width"]), float(a["height"]))
        polys.append([(x, y), (x + w, y), (x + w, y + h), (x, y + h)])
    for tag in re.findall(r"<polygon [^>]*/>", svg):
        a = _attrs(tag)
        if a.get("stroke") == "currentColor" and "surface" in a.get("fill", ""):
            polys.append(_points(a["points"]))  # a diamond node
    return polys


def _edge_segments(svg: str) -> list[tuple[float, float, float, float]]:
    """Every straight edge (``<line>``) and each leg of every routed edge
    (``<polyline>``); arrowhead polygons are not edges and are ignored."""
    segs = []
    for tag in re.findall(r"<line [^>]*/>", svg):
        a = _attrs(tag)
        segs.append((float(a["x1"]), float(a["y1"]),
                     float(a["x2"]), float(a["y2"])))
    for tag in re.findall(r"<polyline [^>]*/>", svg):
        pts = _points(_attrs(tag)["points"])
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            segs.append((x1, y1, x2, y2))
    return segs


def _segment_enters(ax, ay, bx, by, poly, eps: float) -> bool:
    """True iff segment A->B crosses the interior of convex ``poly`` after the
    interior is shrunk inward by ``eps`` (so an edge that merely lands on a
    border, as endpoints legitimately do, does not count as tunnelling)."""
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    dx, dy = bx - ax, by - ay
    t0, t1, n = 0.0, 1.0, len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        nx, ny = -(y1 - y0), (x1 - x0)              # a normal to this edge
        if (cx - x0) * nx + (cy - y0) * ny < 0:      # aim it into the polygon
            nx, ny = -nx, -ny
        mag = math.hypot(nx, ny)
        nx, ny = nx / mag, ny / mag
        f0 = (ax - x0) * nx + (ay - y0) * ny - eps   # inside <=> f0 + t*fd >= 0
        fd = dx * nx + dy * ny
        if abs(fd) < 1e-12:
            if f0 < 0:
                return False                          # runs outside this side
        else:
            t = -f0 / fd
            if fd > 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
            if t0 > t1:
                return False
    return t1 - t0 > 1e-7


def _flowchart_fences() -> list[tuple[str, str]]:
    out = []
    for path in sorted((ROOT / "docs").glob("*.md")):
        for fence_line, body in _mermaid_blocks(path.read_text(encoding="utf-8")):
            head = next((ln.strip() for ln in body.splitlines()
                         if ln.strip() and not ln.strip().startswith("%%")), "")
            if head.startswith("flowchart"):
                out.append((f"{path.name}:{fence_line}", body))
    return out


def test_no_edge_segment_tunnels_through_a_node_box(mermaid):
    fences = _flowchart_fences()
    # The syllabus prerequisite map (the real skip-layer DAG) must be covered.
    assert any(name.startswith("syllabus.md") for name, _ in fences)
    for name, body in fences:
        svg = mermaid.render_diagram(body)
        polys = _node_polys(svg)
        assert polys, name
        for seg in _edge_segments(svg):
            for poly in polys:
                assert not _segment_enters(*seg, poly, 1.0), (
                    f"{name}: edge segment {seg} passes through node box {poly}")
