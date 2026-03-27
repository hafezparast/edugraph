#!/usr/bin/env python3
"""
Generate self-contained D3.js force-directed graph visualizations.

Usage:
    python visualize.py                    # generate all graphs
    python visualize.py malaysia-k12       # generate one graph
    python visualize.py igcse-math         # generate one graph
"""

import json
import os
import sys

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")

GRAPHS = {
    "malaysia-k12": {
        "data": "data/malaysia-k12.json",
        "output": "malaysia-math.html",
        "title": "Malaysia Mathematics",
        "subtitle": "Year 1 to STPM",
    },
    "malaysia-sejarah": {
        "data": "data/malaysia-sejarah.json",
        "output": "malaysia-sejarah.html",
        "title": "Malaysia History (Sejarah)",
        "subtitle": "Year 4 to STPM",
    },
    "malaysia-cs": {
        "data": "data/malaysia-cs.json",
        "output": "malaysia-cs.html",
        "title": "Malaysia Computer Science",
        "subtitle": "ASK (Form 1-3) + Sains Komputer (Form 4-5)",
    },
    "malaysia-science": {
        "data": "data/malaysia-science.json",
        "output": "malaysia-science.html",
        "title": "Malaysia Science",
        "subtitle": "Year 1 to Form 3",
    },
    "malaysia-physics": {
        "data": "data/malaysia-physics.json",
        "output": "malaysia-physics.html",
        "title": "Malaysia Physics",
        "subtitle": "Form 4-5 + STPM",
    },
    "malaysia-chemistry": {
        "data": "data/malaysia-chemistry.json",
        "output": "malaysia-chemistry.html",
        "title": "Malaysia Chemistry",
        "subtitle": "Form 4-5 + STPM",
    },
    "malaysia-biology": {
        "data": "data/malaysia-biology.json",
        "output": "malaysia-biology.html",
        "title": "Malaysia Biology",
        "subtitle": "Form 4-5 + STPM",
    },
    "malaysia-economics": {
        "data": "data/malaysia-economics.json",
        "output": "malaysia-economics.html",
        "title": "Malaysia Economics",
        "subtitle": "STPM (944)",
    },
    "malaysia-accounting": {
        "data": "data/malaysia-accounting.json",
        "output": "malaysia-accounting.html",
        "title": "Malaysia Accounting",
        "subtitle": "STPM (948)",
    },
    "malaysia-math-m": {
        "data": "data/malaysia-math-m.json",
        "output": "malaysia-math-m.html",
        "title": "Malaysia Mathematics M",
        "subtitle": "STPM (950)",
    },
    "igcse-math": {
        "data": "data/igcse-math.json",
        "output": "igcse-math.html",
        "title": "IGCSE Mathematics",
        "subtitle": "Cambridge 0580 — Core & Extended + Add Math 0606",
    },
    "igcse-physics": {
        "data": "data/igcse-physics.json",
        "output": "igcse-physics.html",
        "title": "IGCSE Physics",
        "subtitle": "Cambridge 0625",
    },
    "igcse-chemistry": {
        "data": "data/igcse-chemistry.json",
        "output": "igcse-chemistry.html",
        "title": "IGCSE Chemistry",
        "subtitle": "Cambridge 0620",
    },
    "igcse-biology": {
        "data": "data/igcse-biology.json",
        "output": "igcse-biology.html",
        "title": "IGCSE Biology",
        "subtitle": "Cambridge 0610",
    },
    "igcse-compsci": {
        "data": "data/igcse-compsci.json",
        "output": "igcse-compsci.html",
        "title": "IGCSE Computer Science & ICT",
        "subtitle": "Cambridge 0478 + 0417",
    },
    "igcse-business": {
        "data": "data/igcse-business.json",
        "output": "igcse-business.html",
        "title": "IGCSE Business Studies",
        "subtitle": "Cambridge 0450",
    },
    "lang-en": {"data": "data/lang-en.json", "output": "lang-en.html", "title": "English", "subtitle": "CEFR A1.1 — C2.2"},
    "lang-ms": {"data": "data/lang-ms.json", "output": "lang-ms.html", "title": "Bahasa Malaysia", "subtitle": "CEFR A1.1 — C2.2"},
    "lang-de": {"data": "data/lang-de.json", "output": "lang-de.html", "title": "German (Deutsch)", "subtitle": "CEFR A1.1 — C2.2"},
    "lang-fa": {"data": "data/lang-fa.json", "output": "lang-fa.html", "title": "Farsi (فارسی)", "subtitle": "CEFR A1.1 — C2.2"},
    "lang-ar": {"data": "data/lang-ar.json", "output": "lang-ar.html", "title": "Arabic (العربية)", "subtitle": "CEFR A1.1 — C2.2"},
    "lang-es": {"data": "data/lang-es.json", "output": "lang-es.html", "title": "Spanish (Español)", "subtitle": "CEFR A1.1 — C2.2"},
    "lang-fr": {"data": "data/lang-fr.json", "output": "lang-fr.html", "title": "French (Français)", "subtitle": "CEFR A1.1 — C2.2"},
    "lang-ru": {"data": "data/lang-ru.json", "output": "lang-ru.html", "title": "Russian (Русский)", "subtitle": "CEFR A1.1 — C2.2"},
    "lang-ja": {"data": "data/lang-ja.json", "output": "lang-ja.html", "title": "Japanese (日本語)", "subtitle": "CEFR A1.1 — C2.2"},
    "lang-ko": {"data": "data/lang-ko.json", "output": "lang-ko.html", "title": "Korean (한국어)", "subtitle": "CEFR A1.1 — C2.2"},
    "lang-tr": {"data": "data/lang-tr.json", "output": "lang-tr.html", "title": "Turkish (Türkçe)", "subtitle": "CEFR A1.1 — C2.2"},
    "lang-zh": {"data": "data/lang-zh.json", "output": "lang-zh.html", "title": "Mandarin Chinese (中文)", "subtitle": "CEFR A1.1 — C2.2"},
}


def generate(name, config):
    data_path = os.path.join(BASE_DIR, config["data"])
    output_path = os.path.join(BASE_DIR, config["output"])

    with open(data_path) as f:
        data = json.load(f)

    books = {b["id"]: b for b in data["books"]}
    d3_nodes = []
    for n in data["nodes"]:
        b = books.get(n["book"], {})
        d3_nodes.append({
            "id": n["id"],
            "label": n["label"],
            "color": b.get("color", "#666"),
            "book": n["book"],
            "bookName": b.get("name", ""),
            "bookOrder": b.get("order", 0),
            "r": 4 + min(b.get("order", 0), 20) * 0.8,
            "pages": n.get("pages", ""),
            "description": n.get("description", ""),
        })

    d3_edges = [{"source": e["source"], "target": e["target"]} for e in data["edges"]]

    # Auto-detect topic strands from node labels
    STRAND_KEYWORDS = [
        ("Numbers & Counting", ["number", "counting", "integer", "digit", "place value"]),
        ("Arithmetic", ["addition", "subtraction", "multiplication", "division", "operation"]),
        ("Fractions", ["fraction", "improper", "mixed number"]),
        ("Decimals", ["decimal", "hundredths"]),
        ("Percentages", ["percent"]),
        ("Algebra", ["algebra", "expression", "variable", "unknown", "substitution", "bracket", "expansion", "factoris"]),
        ("Equations", ["equation", "simultaneous", "linear eq", "quadratic eq", "formula"]),
        ("Inequalities", ["inequalit", "region"]),
        ("Functions & Graphs", ["function", "graph", "gradient", "curve", "parabola", "reciprocal", "hyperbola"]),
        ("Indices & Logarithms", ["indices", "index", "logarithm", "exponential", "surd", "power", "root"]),
        ("Sequences & Series", ["sequence", "pattern", "progression", "series", "binomial"]),
        ("Ratio & Proportion", ["ratio", "proportion", "rate", "variation", "scale"]),
        ("Money & Finance", ["money", "currency", "profit", "loss", "discount", "interest", "dividend", "invoice", "tax", "insurance", "invest", "credit", "debt", "financial"]),
        ("Time", ["time", "duration", "calendar", "clock", "hour", "minute", "day", "week", "month", "year", "century", "decade", "time zone"]),
        ("Measurement", ["length", "mass", "volume", "weight", "litre", "gram", "metre", "kilometre", "centimetre", "millimetre", "unit"]),
        ("Geometry", ["angle", "line", "triangle", "quadrilateral", "polygon", "circle", "shape", "prism", "construction", "congruence", "loci"]),
        ("Symmetry & Transformations", ["symmetry", "reflection", "rotation", "translation", "transformation", "enlargement", "tessellation", "isometr"]),
        ("Perimeter, Area & Volume", ["perimeter", "area", "surface", "volume", "sector", "arc"]),
        ("Trigonometry", ["trigonometric", "sine", "cosine", "tangent", "bearing", "circular measure", "radian"]),
        ("Pythagoras & Similarity", ["pythagoras", "similar", "congruence"]),
        ("Coordinate Geometry", ["coordinate", "midpoint", "distance", "cartesian"]),
        ("Vectors & Matrices", ["vector", "matri"]),
        ("Statistics", ["data", "average", "mean", "median", "mode", "range", "frequency", "histogram", "pie chart", "bar chart", "pictograph", "scatter", "dispersion", "quartile", "cumulative"]),
        ("Probability", ["probability", "likelihood", "certain", "impossible", "likely", "tree diagram", "venn", "conditional", "combined event", "permutation", "combination", "factorial"]),
        ("Calculus", ["derivative", "differentiation", "integration", "integral", "limit", "continuity", "maclaurin", "differential equation", "gradient function", "chain rule", "product rule", "quotient rule", "stationary"]),
        ("Kinematics", ["kinematic", "velocity", "acceleration", "displacement"]),
        ("Sets & Logic", ["set", "venn diagram", "universal", "complement", "union", "intersection", "statement", "argument", "logical"]),
        ("Number Bases", ["number base", "binary"]),
        ("Graph Theory", ["network", "graph theory"]),
        ("Mathematical Modeling", ["model"]),
    ]

    STRAND_COLORS = [
        "#ef4444", "#f97316", "#f59e0b", "#eab308", "#84cc16",
        "#22c55e", "#10b981", "#14b8a6", "#06b6d4", "#0ea5e9",
        "#3b82f6", "#6366f1", "#8b5cf6", "#a855f7", "#d946ef",
        "#ec4899", "#f43f5e", "#fb923c", "#facc15", "#a78bfa",
        "#34d399", "#22d3ee", "#c084fc", "#fbbf24", "#4ade80",
        "#f472b6", "#818cf8", "#2dd4bf", "#fb7185", "#d97706",
    ]

    def classify_node(n):
        label = n["label"].lower()
        desc = n.get("description", "").lower()
        text = label + " " + desc
        for strand_name, keywords in STRAND_KEYWORDS:
            for kw in keywords:
                if kw in text:
                    return strand_name
        return "Other"

    # Build strand groups
    from collections import OrderedDict
    strand_nodes = OrderedDict()
    for n in d3_nodes:
        orig = next((x for x in data["nodes"] if x["id"] == n["id"]), n)
        strand = classify_node(orig)
        strand_nodes.setdefault(strand, []).append(n["id"])
        n["strand"] = strand

    # Assign strand colors
    strand_color_map = {}
    for i, strand_name in enumerate(strand_nodes.keys()):
        strand_color_map[strand_name] = STRAND_COLORS[i % len(STRAND_COLORS)]

    strands_list = [
        {"name": name, "color": strand_color_map[name], "nodeIds": ids}
        for name, ids in strand_nodes.items()
        if len(ids) > 0
    ]

    # Group books by education level for collapsible groups
    book_groups = OrderedDict()
    for b in data["books"]:
        name = b["name"]
        if any(x in name for x in ["Y1", "Y2", "Y3", "Y4", "Y5", "Y6", "Year"]):
            group = "Primary (Year 1-6)"
        elif any(x in name for x in ["Form 1", "Form 2", "Form 3"]):
            group = "Lower Secondary (Form 1-3)"
        elif any(x in name for x in ["Form 4", "Form 5"]):
            group = "Upper Secondary (Form 4-5)"
        elif any(x in name for x in ["Add Math", "AM"]):
            group = "Additional Mathematics"
        elif "STPM" in name:
            group = "Pre-University (STPM)"
        elif any(x in name for x in ["Number", "Algebra", "Geometry", "Data", "Fraction", "Equation",
                                       "Mensuration", "Probability", "Sequence", "Line", "Quadratic"]):
            group = "IGCSE Math Core+Extended"
        elif any(x in name for x in ["Pythagoras", "Average", "Further", "Trigonometry", "Ratio",
                                       "Scatter", "Money", "Curved", "Symmetry", "Histogram",
                                       "More Equation", "Transform", "Advanced"]):
            group = "IGCSE Math Core+Extended"
        elif any(x in name for x in ["(AM)", "Calculus", "Kinematics", "Vectors (AM)", "Polynomials",
                                       "Logarithm", "Circle Coord", "Circular Measure", "Permutation",
                                       "Series", "Differentiation", "Integration"]):
            group = "IGCSE Additional Mathematics"
        else:
            group = "Other"
        book_groups.setdefault(group, []).append(b)

    nodes_json = json.dumps(d3_nodes)
    edges_json = json.dumps(d3_edges)
    books_json = json.dumps(data["books"])
    strands_json = json.dumps(strands_list)
    book_groups_json = json.dumps(book_groups)
    page_title = config["title"]
    page_subtitle = config["subtitle"]

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EduGraph — """ + page_title + """</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
:root {
  --bg: #08090e;
  --surface: rgba(12,14,24,0.94);
  --border: rgba(255,255,255,0.06);
  --text: #e8e4dc;
  --text2: #8a8697;
  --text3: #55516a;
  --gold: #ffc857;
  --topbar: 52px;
  --sidebar: 230px;
  --detail: 300px;
}
html, body { height: 100%; background: var(--bg); color: var(--text); font-family: 'DM Sans', sans-serif; font-size: 13px; overflow: hidden; }

/* Grain */
body::after { content: ''; position: fixed; inset: 0; opacity: 0.035; background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E"); pointer-events: none; z-index: 9999; }

/* Topbar */
.topbar { position: fixed; top: 0; left: 0; right: 0; height: var(--topbar); display: flex; align-items: center; justify-content: space-between; padding: 0 18px; background: rgba(8,9,14,0.92); backdrop-filter: blur(16px); border-bottom: 1px solid var(--border); z-index: 200; }
.topbar-left { display: flex; align-items: baseline; gap: 12px; }
.topbar h1 { font-family: 'Instrument Serif', serif; font-size: 22px; font-weight: 400; color: var(--gold); }
.topbar .sub { font-size: 10px; color: var(--text3); text-transform: uppercase; letter-spacing: 1px; }
.topbar-right { display: flex; align-items: center; gap: 6px; }
.stats { display: flex; gap: 14px; margin-right: 12px; }
.stat-n { font-family: 'Instrument Serif', serif; font-size: 17px; color: var(--gold); }
.stat-l { font-size: 9px; color: var(--text3); text-transform: uppercase; letter-spacing: 0.5px; margin-left: 3px; }
.nav-btn { background: rgba(255,255,255,0.04); border: 1px solid var(--border); color: var(--text2); padding: 4px 10px; border-radius: 5px; font-size: 10px; font-family: 'DM Sans', sans-serif; cursor: pointer; text-decoration: none; text-transform: uppercase; letter-spacing: 0.5px; transition: all 0.15s; }
.nav-btn:hover { background: rgba(255,200,87,0.08); border-color: rgba(255,200,87,0.15); color: var(--gold); }

/* Sidebar */
.sidebar { position: fixed; top: var(--topbar); left: 0; bottom: 0; width: var(--sidebar); background: var(--surface); border-right: 1px solid var(--border); overflow-y: auto; z-index: 100; padding: 12px; display: flex; flex-direction: column; gap: 10px; }
.sidebar::-webkit-scrollbar { width: 3px; }
.sidebar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 2px; }
.sec-title { font-family: 'Instrument Serif', serif; font-size: 13px; margin-bottom: 6px; display: flex; align-items: center; gap: 6px; }
.sec-title::before { content: ''; width: 2px; height: 11px; background: var(--gold); border-radius: 1px; }

.search-box { width: 100%; padding: 7px 10px 7px 28px; background: rgba(255,255,255,0.04); border: 1px solid var(--border); border-radius: 6px; color: var(--text); font-family: 'DM Sans', sans-serif; font-size: 12px; outline: none; }
.search-box::placeholder { color: var(--text3); }
.search-box:focus { border-color: rgba(255,200,87,0.25); }
.search-wrap { position: relative; }
.search-wrap::before { content: '⌕'; position: absolute; left: 9px; top: 50%; transform: translateY(-50%); color: var(--text3); font-size: 13px; }

/* Tabs */
.tab-bar { display: flex; gap: 0; margin-bottom: 8px; border-bottom: 1px solid var(--border); }
.tab-btn { flex: 1; background: none; border: none; border-bottom: 2px solid transparent; color: var(--text3); padding: 6px 4px; font-size: 10px; font-family: 'DM Sans', sans-serif; cursor: pointer; text-transform: uppercase; letter-spacing: 0.8px; transition: all 0.15s; }
.tab-btn:hover { color: var(--text2); }
.tab-btn.active { color: var(--gold); border-bottom-color: var(--gold); }
.tab-content { display: none; }
.tab-content.active { display: block; }

.book-btns { display: flex; gap: 3px; margin-bottom: 6px; }
.book-btn { flex: 1; background: rgba(255,255,255,0.03); border: 1px solid var(--border); color: var(--text3); padding: 3px; border-radius: 4px; font-size: 9px; font-family: 'DM Sans', sans-serif; cursor: pointer; text-transform: uppercase; letter-spacing: 0.5px; }
.book-btn:hover { color: var(--text2); }

/* Collapsible groups */
.group-header { display: flex; align-items: center; gap: 5px; padding: 5px 4px; cursor: pointer; user-select: none; border-radius: 4px; margin-top: 4px; transition: background 0.12s; }
.group-header:hover { background: rgba(255,255,255,0.03); }
.group-arrow { font-size: 8px; color: var(--text3); transition: transform 0.2s; width: 12px; text-align: center; }
.group-header.collapsed .group-arrow { transform: rotate(-90deg); }
.group-label { font-size: 10px; color: var(--text2); font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; flex: 1; }
.group-cnt { font-size: 9px; color: var(--text3); }
.group-body { overflow: hidden; transition: max-height 0.25s ease; }
.group-header.collapsed + .group-body { max-height: 0 !important; overflow: hidden; }

.book-list { display: flex; flex-direction: column; gap: 1px; }
.book-item { display: flex; align-items: center; gap: 6px; padding: 3px 5px 3px 16px; border-radius: 4px; cursor: pointer; transition: all 0.12s; user-select: none; }
.book-item:hover { background: rgba(255,255,255,0.03); }
.book-item.off { opacity: 0.2; }
.book-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; transition: transform 0.15s; }
.book-item:not(.off) .book-dot { box-shadow: 0 0 5px currentColor; }
.book-name { font-size: 10px; color: var(--text2); flex: 1; }
.book-item:not(.off) .book-name { color: var(--text); }
.book-cnt { font-size: 9px; color: var(--text3); }

/* Strand items */
.strand-item { display: flex; align-items: center; gap: 6px; padding: 3px 5px 3px 16px; border-radius: 4px; cursor: pointer; transition: all 0.12s; user-select: none; }
.strand-item:hover { background: rgba(255,255,255,0.03); }
.strand-item.off { opacity: 0.2; }
.strand-dot { width: 7px; height: 7px; border-radius: 3px; flex-shrink: 0; }
.strand-name { font-size: 10px; color: var(--text2); flex: 1; }
.strand-item:not(.off) .strand-name { color: var(--text); }
.strand-cnt { font-size: 9px; color: var(--text3); }

.controls { padding-top: 8px; border-top: 1px solid var(--border); display: flex; flex-direction: column; gap: 6px; }
.ctrl-row { display: flex; align-items: center; justify-content: space-between; }
.ctrl-label { font-size: 10px; color: var(--text3); text-transform: uppercase; letter-spacing: 0.5px; }
.ctrl-slider { -webkit-appearance: none; width: 90px; height: 3px; background: rgba(255,255,255,0.1); border-radius: 2px; outline: none; }
.ctrl-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 12px; height: 12px; background: var(--gold); border-radius: 50%; cursor: pointer; }

.hint { font-size: 9px; color: var(--text3); line-height: 1.6; padding-top: 8px; border-top: 1px solid var(--border); }
.hint b { color: var(--text2); font-weight: 500; }

/* Graph SVG */
#graph-container { position: fixed; top: var(--topbar); left: var(--sidebar); right: 0; bottom: 0; transition: right 0.3s; }
#graph-container.detail-open { right: var(--detail); }
svg { width: 100%; height: 100%; display: block; }

/* Detail panel */
.detail { position: fixed; top: var(--topbar); right: calc(-1 * var(--detail)); bottom: 0; width: var(--detail); background: var(--surface); border-left: 1px solid var(--border); z-index: 100; overflow-y: auto; padding: 20px 16px; transition: right 0.3s; }
.detail.open { right: 0; }
.detail::-webkit-scrollbar { width: 3px; }
.detail::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 2px; }
.detail-close { position: absolute; top: 12px; right: 12px; width: 24px; height: 24px; border-radius: 5px; background: rgba(255,255,255,0.04); border: 1px solid var(--border); color: var(--text3); cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 12px; }
.detail-close:hover { color: var(--text); }
.detail-badge { display: inline-flex; align-items: center; gap: 5px; padding: 2px 8px; border-radius: 12px; font-size: 9px; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 6px; }
.detail-pages { display: inline-block; padding: 3px 10px; border-radius: 5px; font-family: 'Instrument Serif', serif; font-size: 16px; background: rgba(255,200,87,0.08); color: var(--gold); border: 1px solid rgba(255,200,87,0.12); margin-bottom: 10px; }
.detail-title { font-family: 'Instrument Serif', serif; font-size: 20px; line-height: 1.2; margin-bottom: 14px; }
.conn-section { margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border); }
.conn-head { font-size: 9px; text-transform: uppercase; letter-spacing: 0.8px; color: var(--text3); margin-bottom: 6px; }
.conn-head.prereq { color: #e07a5f; }
.conn-head.leads { color: #81b29a; }
.conn-item { display: flex; align-items: center; gap: 6px; padding: 3px 5px; border-radius: 4px; cursor: pointer; transition: background 0.12s; }
.conn-item:hover { background: rgba(255,255,255,0.04); }
.conn-dot { width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; }
.conn-label { font-size: 11px; color: var(--text2); flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.conn-book { font-size: 8px; color: var(--text3); flex-shrink: 0; }

@media (max-width: 800px) {
  .sidebar { display: none; }
  :root { --sidebar: 0px; }
  .topbar .sub, .stats { display: none; }
}
</style>
</head>
<body>

<header class="topbar">
  <div class="topbar-left">
    <h1>EduGraph</h1>
    <span class="sub">""" + page_subtitle + """</span>
  </div>
  <div class="topbar-right">
    <div class="stats">
      <span><span class="stat-n" id="s-nodes">0</span><span class="stat-l">nodes</span></span>
      <span><span class="stat-n" id="s-edges">0</span><span class="stat-l">edges</span></span>
    </div>
    <a href="index.html" class="nav-btn">Home</a>
  </div>
</header>

<aside class="sidebar">
  <div class="search-wrap">
    <input type="text" class="search-box" id="search" placeholder="Search topics..." autocomplete="off">
  </div>

  <div class="tab-bar">
    <button class="tab-btn active" data-tab="grades">Grades</button>
    <button class="tab-btn" data-tab="topics">Topics</button>
    <button class="tab-btn" data-tab="forces">Forces</button>
  </div>

  <!-- Grades Tab -->
  <div class="tab-content active" id="tab-grades">
    <div class="book-btns">
      <button class="book-btn" id="b-all">All</button>
      <button class="book-btn" id="b-none">None</button>
    </div>
    <div id="grades-list"></div>
  </div>

  <!-- Topics Tab -->
  <div class="tab-content" id="tab-topics">
    <div class="book-btns">
      <button class="book-btn" id="t-all">All</button>
      <button class="book-btn" id="t-none">None</button>
    </div>
    <div id="topics-list"></div>
  </div>

  <!-- Forces Tab -->
  <div class="tab-content" id="tab-forces">
    <div class="sec-title">Physics</div>
    <div class="controls">
      <div class="ctrl-row">
        <span class="ctrl-label">Repulsion</span>
        <input type="range" class="ctrl-slider" id="sl-charge" min="-600" max="-20" value="-120">
      </div>
      <div class="ctrl-row">
        <span class="ctrl-label">Link Dist</span>
        <input type="range" class="ctrl-slider" id="sl-dist" min="15" max="200" value="55">
      </div>
      <div class="ctrl-row">
        <span class="ctrl-label">Gravity</span>
        <input type="range" class="ctrl-slider" id="sl-gravity" min="0" max="100" value="8">
      </div>
      <div class="ctrl-row">
        <span class="ctrl-label">Collision</span>
        <input type="range" class="ctrl-slider" id="sl-collide" min="1" max="30" value="10">
      </div>
    </div>
    <div class="hint">
      <b>Drag</b> nodes — physics responds live<br>
      <b>Scroll</b> to zoom, drag canvas to pan<br>
      <b>Click</b> node for details &amp; neighbors<br>
      <b>Sliders</b> tune forces in real-time
    </div>
  </div>
</aside>

<div id="graph-container">
  <svg id="svg"></svg>
</div>

<div class="detail" id="detail">
  <button class="detail-close" id="detail-close">✕</button>
  <div id="detail-content"></div>
</div>

<script>
const rawNodes = """ + nodes_json + """;
const rawEdges = """ + edges_json + """;
const booksData = """ + books_json + """;
const strandsData = """ + strands_json + """;
const bookGroupsData = """ + book_groups_json + """;

// State
const activeBooks = new Set(booksData.map(b => b.id));
const activeStrands = new Set(strandsData.map(s => s.name));
let filterMode = 'grades'; // 'grades' or 'topics'
let selectedNode = null;

// D3 setup
const container = document.getElementById('graph-container');
const svg = d3.select('#svg');
const g = svg.append('g');

// Arrow marker
svg.append('defs').append('marker')
  .attr('id', 'arrow')
  .attr('viewBox', '0 -4 8 8')
  .attr('refX', 18)
  .attr('refY', 0)
  .attr('markerWidth', 5)
  .attr('markerHeight', 5)
  .attr('orient', 'auto')
  .append('path')
  .attr('d', 'M0,-3L7,0L0,3')
  .attr('fill', '#6b6590');

// Glow marker for highlighted
svg.select('defs').append('marker')
  .attr('id', 'arrow-hl')
  .attr('viewBox', '0 -4 8 8')
  .attr('refX', 18)
  .attr('refY', 0)
  .attr('markerWidth', 6)
  .attr('markerHeight', 6)
  .attr('orient', 'auto')
  .append('path')
  .attr('d', 'M0,-3L7,0L0,3')
  .attr('fill', '#ffc857');

// Build graph data
const nodes = rawNodes.map(d => ({...d}));
const edges = rawEdges.map(d => ({...d}));

// Index
const nodeMap = {};
nodes.forEach(n => { nodeMap[n.id] = n; });

// Links
const linkGroup = g.append('g').attr('class', 'links');
const nodeGroup = g.append('g').attr('class', 'nodes');
const labelGroup = g.append('g').attr('class', 'labels');

let linkEls, nodeEls, labelEls;

function renderGraph() {
  // Filter
  let visibleIds;
  if (filterMode === 'topics') {
    visibleIds = new Set(nodes.filter(n => activeStrands.has(n.strand)).map(n => n.id));
  } else {
    visibleIds = new Set(nodes.filter(n => activeBooks.has(n.book)).map(n => n.id));
  }
  const vNodes = nodes.filter(n => visibleIds.has(n.id));
  const vEdges = edges.filter(e => {
    const sid = typeof e.source === 'object' ? e.source.id : e.source;
    const tid = typeof e.target === 'object' ? e.target.id : e.target;
    return visibleIds.has(sid) && visibleIds.has(tid);
  });

  // Links
  linkEls = linkGroup.selectAll('line').data(vEdges, d => {
    const s = typeof d.source === 'object' ? d.source.id : d.source;
    const t = typeof d.target === 'object' ? d.target.id : d.target;
    return s + '->' + t;
  });
  linkEls.exit().remove();
  linkEls = linkEls.enter().append('line')
    .attr('stroke', '#5a5480')
    .attr('stroke-width', 0.7)
    .attr('stroke-opacity', 0.5)
    .attr('marker-end', 'url(#arrow)')
    .merge(linkEls);

  // Nodes
  nodeEls = nodeGroup.selectAll('circle').data(vNodes, d => d.id);
  nodeEls.exit().remove();
  nodeEls = nodeEls.enter().append('circle')
    .attr('r', d => d.r)
    .attr('fill', d => d.color)
    .attr('fill-opacity', 0.85)
    .attr('stroke', 'none')
    .attr('stroke-width', 2)
    .attr('cursor', 'pointer')
    .on('click', (ev, d) => { ev.stopPropagation(); selectNode(d); })
    .call(d3.drag()
      .on('start', dragStart)
      .on('drag', dragging)
      .on('end', dragEnd))
    .merge(nodeEls)
    .attr('fill', d => d.color);

  // Labels
  labelEls = labelGroup.selectAll('text').data(vNodes, d => d.id);
  labelEls.exit().remove();
  labelEls = labelEls.enter().append('text')
    .attr('font-size', d => Math.max(6, d.r * 0.85))
    .attr('font-family', "'DM Sans', sans-serif")
    .attr('fill', '#a09cac')
    .attr('text-anchor', 'middle')
    .attr('dy', d => d.r + 10)
    .attr('pointer-events', 'none')
    .text(d => d.label.length > 22 ? d.label.slice(0, 20) + '…' : d.label)
    .merge(labelEls);

  // Update simulation
  simulation.nodes(vNodes);
  simulation.force('link').links(vEdges);
  simulation.alpha(0.6).restart();

  updateStats(vNodes.length, vEdges.length);
}

// Force simulation
const simulation = d3.forceSimulation()
  .force('link', d3.forceLink().id(d => d.id).distance(55).strength(0.3))
  .force('charge', d3.forceManyBody().strength(-120).distanceMax(400))
  .force('center', d3.forceCenter())
  .force('collide', d3.forceCollide().radius(10).strength(0.7))
  .force('x', d3.forceX().strength(0.02))
  .force('y', d3.forceY().strength(0.02))
  .alphaDecay(0.015)
  .velocityDecay(0.35)
  .on('tick', ticked);

function ticked() {
  linkEls
    .attr('x1', d => d.source.x)
    .attr('y1', d => d.source.y)
    .attr('x2', d => d.target.x)
    .attr('y2', d => d.target.y);
  nodeEls
    .attr('cx', d => d.x)
    .attr('cy', d => d.y);
  labelEls
    .attr('x', d => d.x)
    .attr('y', d => d.y);
}

// Zoom
const zoom = d3.zoom()
  .scaleExtent([0.05, 8])
  .on('zoom', (ev) => { g.attr('transform', ev.transform); });
svg.call(zoom);

// Resize
function resize() {
  const w = container.clientWidth;
  const h = container.clientHeight;
  svg.attr('viewBox', [-w/2, -h/2, w, h]);
  simulation.force('center', d3.forceCenter(0, 0));
}
window.addEventListener('resize', resize);
resize();

// Drag
function dragStart(ev, d) {
  if (!ev.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x; d.fy = d.y;
}
function dragging(ev, d) {
  d.fx = ev.x; d.fy = ev.y;
}
function dragEnd(ev, d) {
  if (!ev.active) simulation.alphaTarget(0);
  d.fx = null; d.fy = null;
}

// Selection & highlighting
function selectNode(d) {
  selectedNode = d;
  const neighbors = new Set([d.id]);
  const prereqEdges = new Set();
  const leadsEdges = new Set();

  edges.forEach(e => {
    const sid = typeof e.source === 'object' ? e.source.id : e.source;
    const tid = typeof e.target === 'object' ? e.target.id : e.target;
    if (sid === d.id) { neighbors.add(tid); leadsEdges.add(sid + '->' + tid); }
    if (tid === d.id) { neighbors.add(sid); prereqEdges.add(sid + '->' + tid); }
  });

  nodeEls.attr('fill-opacity', n => neighbors.has(n.id) ? 1 : 0.06)
    .attr('stroke', n => n.id === d.id ? '#ffc857' : 'none')
    .attr('stroke-width', n => n.id === d.id ? 2.5 : 0);
  labelEls.attr('fill', n => neighbors.has(n.id) ? '#e8e4dc' : '#1a1830')
    .attr('font-weight', n => n.id === d.id ? 600 : 400);
  linkEls.attr('stroke', e => {
      const k = (typeof e.source === 'object' ? e.source.id : e.source) + '->' + (typeof e.target === 'object' ? e.target.id : e.target);
      if (prereqEdges.has(k)) return '#e07a5f';
      if (leadsEdges.has(k)) return '#81b29a';
      return '#5a5480';
    })
    .attr('stroke-opacity', e => {
      const k = (typeof e.source === 'object' ? e.source.id : e.source) + '->' + (typeof e.target === 'object' ? e.target.id : e.target);
      return (prereqEdges.has(k) || leadsEdges.has(k)) ? 0.9 : 0.04;
    })
    .attr('stroke-width', e => {
      const k = (typeof e.source === 'object' ? e.source.id : e.source) + '->' + (typeof e.target === 'object' ? e.target.id : e.target);
      return (prereqEdges.has(k) || leadsEdges.has(k)) ? 1.8 : 0.7;
    })
    .attr('marker-end', e => {
      const k = (typeof e.source === 'object' ? e.source.id : e.source) + '->' + (typeof e.target === 'object' ? e.target.id : e.target);
      return (prereqEdges.has(k) || leadsEdges.has(k)) ? 'url(#arrow-hl)' : 'url(#arrow)';
    });

  showDetail(d, prereqEdges, leadsEdges);
}

function clearSelection() {
  selectedNode = null;
  nodeEls.attr('fill-opacity', 0.85).attr('stroke', 'none');
  labelEls.attr('fill', '#a09cac').attr('font-weight', 400);
  linkEls.attr('stroke', '#5a5480').attr('stroke-opacity', 0.5).attr('stroke-width', 0.7).attr('marker-end', 'url(#arrow)');
  document.getElementById('detail').classList.remove('open');
  document.getElementById('graph-container').classList.remove('detail-open');
}

svg.on('click', () => clearSelection());

// Detail panel
function showDetail(d, prereqEdges, leadsEdges) {
  const panel = document.getElementById('detail');
  const content = document.getElementById('detail-content');
  document.getElementById('graph-container').classList.add('detail-open');

  const prereqs = [];
  const leads = [];
  edges.forEach(e => {
    const sid = typeof e.source === 'object' ? e.source.id : e.source;
    const tid = typeof e.target === 'object' ? e.target.id : e.target;
    if (tid === d.id && nodeMap[sid]) prereqs.push(nodeMap[sid]);
    if (sid === d.id && nodeMap[tid]) leads.push(nodeMap[tid]);
  });

  content.innerHTML = `
    <div class="detail-badge" style="background:${d.color}18;color:${d.color};border:1px solid ${d.color}30">
      <span style="width:5px;height:5px;border-radius:50%;background:${d.color};display:inline-block"></span>
      ${d.bookName}
    </div>
    ${d.pages ? `<div class="detail-pages">p. ${d.pages}</div>` : ''}
    <div class="detail-title">${d.label}</div>
    ${prereqs.length ? `
      <div class="conn-section">
        <div class="conn-head prereq">▲ Prerequisites (${prereqs.length})</div>
        ${prereqs.map(n => `<div class="conn-item" data-id="${n.id}"><span class="conn-dot" style="background:${n.color}"></span><span class="conn-label">${n.label}</span><span class="conn-book">${n.bookName}</span></div>`).join('')}
      </div>
    ` : '<div class="conn-section"><div class="conn-head" style="color:var(--gold)">★ Starting point</div></div>'}
    ${leads.length ? `
      <div class="conn-section">
        <div class="conn-head leads">▼ Leads to (${leads.length})</div>
        ${leads.map(n => `<div class="conn-item" data-id="${n.id}"><span class="conn-dot" style="background:${n.color}"></span><span class="conn-label">${n.label}</span><span class="conn-book">${n.bookName}</span></div>`).join('')}
      </div>
    ` : ''}
  `;

  content.querySelectorAll('.conn-item').forEach(el => {
    el.addEventListener('click', () => {
      const n = nodeMap[el.dataset.id];
      if (n) { selectNode(n); }
    });
  });

  panel.classList.add('open');
}

document.getElementById('detail-close').addEventListener('click', clearSelection);

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
  });
});

// Book counts
const bookCounts = {};
nodes.forEach(n => { bookCounts[n.book] = (bookCounts[n.book] || 0) + 1; });

// === GRADES TAB: books grouped by education level, collapsible ===
const gradesListEl = document.getElementById('grades-list');
Object.entries(bookGroupsData).forEach(([groupName, groupBooks]) => {
  const totalInGroup = groupBooks.reduce((s, b) => s + (bookCounts[b.id] || 0), 0);
  if (totalInGroup === 0) return;

  // Group header
  const header = document.createElement('div');
  header.className = 'group-header';
  header.innerHTML = `<span class="group-arrow">▼</span><span class="group-label">${groupName}</span><span class="group-cnt">${totalInGroup}</span>`;

  // Group body
  const body = document.createElement('div');
  body.className = 'group-body';
  body.style.maxHeight = '500px';

  const list = document.createElement('div');
  list.className = 'book-list';

  groupBooks.forEach(b => {
    const el = document.createElement('div');
    el.className = 'book-item';
    el.dataset.id = b.id;
    el.innerHTML = `<span class="book-dot" style="background:${b.color};color:${b.color}"></span><span class="book-name">${b.name}</span><span class="book-cnt">${bookCounts[b.id] || 0}</span>`;
    el.addEventListener('click', (ev) => {
      ev.stopPropagation();
      if (activeBooks.has(b.id)) { activeBooks.delete(b.id); el.classList.add('off'); }
      else { activeBooks.add(b.id); el.classList.remove('off'); }
      filterMode = 'grades';
      renderGraph();
    });
    list.appendChild(el);
  });

  body.appendChild(list);
  header.addEventListener('click', () => { header.classList.toggle('collapsed'); });

  gradesListEl.appendChild(header);
  gradesListEl.appendChild(body);
});

document.getElementById('b-all').addEventListener('click', () => {
  booksData.forEach(b => activeBooks.add(b.id));
  document.querySelectorAll('#grades-list .book-item').forEach(el => el.classList.remove('off'));
  filterMode = 'grades';
  renderGraph();
});
document.getElementById('b-none').addEventListener('click', () => {
  activeBooks.clear();
  document.querySelectorAll('#grades-list .book-item').forEach(el => el.classList.add('off'));
  filterMode = 'grades';
  renderGraph();
});

// === TOPICS TAB: strands grouped by math domain, collapsible ===
const topicsListEl = document.getElementById('topics-list');
const strandDomains = {
  'Number & Arithmetic': ['Numbers & Counting', 'Arithmetic', 'Fractions', 'Decimals', 'Percentages', 'Number Bases'],
  'Algebra': ['Algebra', 'Equations', 'Inequalities', 'Functions & Graphs', 'Indices & Logarithms', 'Sequences & Series'],
  'Geometry & Measure': ['Geometry', 'Symmetry & Transformations', 'Perimeter, Area & Volume', 'Coordinate Geometry', 'Pythagoras & Similarity', 'Trigonometry'],
  'Data & Probability': ['Statistics', 'Probability', 'Sets & Logic'],
  'Applied': ['Money & Finance', 'Time', 'Measurement', 'Ratio & Proportion', 'Calculus', 'Kinematics', 'Vectors & Matrices', 'Graph Theory', 'Mathematical Modeling'],
};

// Build strand lookup
const strandNodeIds = {};
strandsData.forEach(s => { strandNodeIds[s.name] = new Set(s.nodeIds); });

Object.entries(strandDomains).forEach(([domain, strandNames]) => {
  const domainStrands = strandNames.filter(sn => strandNodeIds[sn] && strandNodeIds[sn].size > 0);
  if (domainStrands.length === 0) return;

  const totalInDomain = domainStrands.reduce((s, sn) => s + (strandNodeIds[sn] ? strandNodeIds[sn].size : 0), 0);

  const header = document.createElement('div');
  header.className = 'group-header';
  header.innerHTML = `<span class="group-arrow">▼</span><span class="group-label">${domain}</span><span class="group-cnt">${totalInDomain}</span>`;

  const body = document.createElement('div');
  body.className = 'group-body';
  body.style.maxHeight = '500px';

  const list = document.createElement('div');
  list.className = 'book-list';

  domainStrands.forEach(sn => {
    const strand = strandsData.find(s => s.name === sn);
    if (!strand) return;
    const el = document.createElement('div');
    el.className = 'strand-item';
    el.dataset.strand = sn;
    el.innerHTML = `<span class="strand-dot" style="background:${strand.color}"></span><span class="strand-name">${sn}</span><span class="strand-cnt">${strand.nodeIds.length}</span>`;
    el.addEventListener('click', (ev) => {
      ev.stopPropagation();
      if (activeStrands.has(sn)) { activeStrands.delete(sn); el.classList.add('off'); }
      else { activeStrands.add(sn); el.classList.remove('off'); }
      filterMode = 'topics';
      renderGraph();
    });
    list.appendChild(el);
  });

  body.appendChild(list);
  header.addEventListener('click', () => { header.classList.toggle('collapsed'); });

  topicsListEl.appendChild(header);
  topicsListEl.appendChild(body);
});

// Also add "Other" strand if it exists
const otherStrand = strandsData.find(s => s.name === 'Other');
if (otherStrand && otherStrand.nodeIds.length > 0) {
  const el = document.createElement('div');
  el.className = 'strand-item';
  el.dataset.strand = 'Other';
  el.innerHTML = `<span class="strand-dot" style="background:${otherStrand.color}"></span><span class="strand-name">Other</span><span class="strand-cnt">${otherStrand.nodeIds.length}</span>`;
  el.addEventListener('click', (ev) => {
    ev.stopPropagation();
    if (activeStrands.has('Other')) { activeStrands.delete('Other'); el.classList.add('off'); }
    else { activeStrands.add('Other'); el.classList.remove('off'); }
    filterMode = 'topics';
    renderGraph();
  });
  topicsListEl.appendChild(el);
}

document.getElementById('t-all').addEventListener('click', () => {
  strandsData.forEach(s => activeStrands.add(s.name));
  document.querySelectorAll('.strand-item').forEach(el => el.classList.remove('off'));
  filterMode = 'topics';
  renderGraph();
});
document.getElementById('t-none').addEventListener('click', () => {
  activeStrands.clear();
  document.querySelectorAll('.strand-item').forEach(el => el.classList.add('off'));
  filterMode = 'topics';
  renderGraph();
});

// Force sliders
document.getElementById('sl-charge').addEventListener('input', function() {
  simulation.force('charge').strength(+this.value);
  simulation.alpha(0.4).restart();
});
document.getElementById('sl-dist').addEventListener('input', function() {
  simulation.force('link').distance(+this.value);
  simulation.alpha(0.4).restart();
});
document.getElementById('sl-gravity').addEventListener('input', function() {
  const v = +this.value / 1000;
  simulation.force('x').strength(v);
  simulation.force('y').strength(v);
  simulation.alpha(0.4).restart();
});
document.getElementById('sl-collide').addEventListener('input', function() {
  simulation.force('collide').radius(+this.value);
  simulation.alpha(0.4).restart();
});

// Search
let searchTimeout;
document.getElementById('search').addEventListener('input', function() {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    const q = this.value.trim().toLowerCase();
    if (!q) { clearSelection(); return; }
    const matches = nodes.filter(n => activeBooks.has(n.book) && (n.label.toLowerCase().includes(q) || n.id.toLowerCase().includes(q)));
    if (matches.length) {
      // Zoom to first match
      const m = matches[0];
      if (m.x != null) {
        const t = d3.zoomIdentity.translate(-m.x * 2 + container.clientWidth/2, -m.y * 2 + container.clientHeight/2).scale(2);
        svg.transition().duration(500).call(zoom.transform, t);
      }
      // Highlight all matches
      const matchIds = new Set(matches.map(n => n.id));
      nodeEls.attr('fill-opacity', n => matchIds.has(n.id) ? 1 : 0.06)
        .attr('stroke', n => matchIds.has(n.id) ? '#ffc857' : 'none')
        .attr('stroke-width', n => matchIds.has(n.id) ? 2 : 0);
      labelEls.attr('fill', n => matchIds.has(n.id) ? '#fff' : '#1a1830');
    }
  }, 250);
});

function updateStats(n, e) {
  document.getElementById('s-nodes').textContent = n;
  document.getElementById('s-edges').textContent = e;
}

// Keyboard
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { clearSelection(); document.getElementById('search').value = ''; }
  if (e.key === '/' && document.activeElement.tagName !== 'INPUT') { e.preventDefault(); document.getElementById('search').focus(); }
});

// Init
renderGraph();
</script>
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)

    print(f"  {name}: {len(d3_nodes)} nodes, {len(d3_edges)} edges → {config['output']}")


if __name__ == "__main__":
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(GRAPHS.keys())
    for name in targets:
        if name not in GRAPHS:
            print(f"Unknown graph: {name}. Available: {', '.join(GRAPHS.keys())}")
            continue
        generate(name, GRAPHS[name])
