#!/usr/bin/env python3
"""
Generate a self-contained D3.js force-directed graph visualization
from the Malaysia K-12 knowledge graph data.

Usage:
    python visualize.py
    # Opens k12-d3.html in browser
"""

import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "malaysia-k12.json")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "k12-d3.html")

with open(DATA_PATH) as f:
    data = json.load(f)

# Build compact nodes/edges for D3
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
        "r": 4 + b.get("order", 0) * 0.8,
        "pages": n.get("pages", ""),
    })

d3_edges = []
for e in data["edges"]:
    d3_edges.append({
        "source": e["source"],
        "target": e["target"],
    })

nodes_json = json.dumps(d3_nodes)
edges_json = json.dumps(d3_edges)
books_json = json.dumps(data["books"])

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EduGraph — Malaysia K-12 (D3.js Force Graph)</title>
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

.book-btns { display: flex; gap: 3px; }
.book-btn { flex: 1; background: rgba(255,255,255,0.03); border: 1px solid var(--border); color: var(--text3); padding: 3px; border-radius: 4px; font-size: 9px; font-family: 'DM Sans', sans-serif; cursor: pointer; text-transform: uppercase; letter-spacing: 0.5px; }
.book-btn:hover { color: var(--text2); }

.book-list { display: flex; flex-direction: column; gap: 1px; }
.book-item { display: flex; align-items: center; gap: 6px; padding: 4px 5px; border-radius: 4px; cursor: pointer; transition: all 0.12s; user-select: none; }
.book-item:hover { background: rgba(255,255,255,0.03); }
.book-item.off { opacity: 0.2; }
.book-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; transition: transform 0.15s; }
.book-item:not(.off) .book-dot { box-shadow: 0 0 6px currentColor; }
.book-name { font-size: 11px; color: var(--text2); flex: 1; }
.book-item:not(.off) .book-name { color: var(--text); }
.book-cnt { font-size: 9px; color: var(--text3); }

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
    <span class="sub">D3.js Force-Directed Graph</span>
  </div>
  <div class="topbar-right">
    <div class="stats">
      <span><span class="stat-n" id="s-nodes">0</span><span class="stat-l">nodes</span></span>
      <span><span class="stat-n" id="s-edges">0</span><span class="stat-l">edges</span></span>
    </div>
    <a href="index.html" class="nav-btn">General</a>
    <a href="k12.html" class="nav-btn">Cytoscape</a>
    <a href="k12-pyvis.html" class="nav-btn">vis.js</a>
  </div>
</header>

<aside class="sidebar">
  <div class="search-wrap">
    <input type="text" class="search-box" id="search" placeholder="Search topics..." autocomplete="off">
  </div>

  <div>
    <div class="sec-title">Textbooks</div>
    <div class="book-btns">
      <button class="book-btn" id="b-all">All</button>
      <button class="book-btn" id="b-none">None</button>
    </div>
    <div class="book-list" id="book-list"></div>
  </div>

  <div class="controls">
    <div class="sec-title">Forces</div>
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

// State
const activeBooks = new Set(booksData.map(b => b.id));
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
  const visibleIds = new Set(nodes.filter(n => activeBooks.has(n.book)).map(n => n.id));
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

// Book sidebar
const bookCounts = {};
nodes.forEach(n => { bookCounts[n.book] = (bookCounts[n.book] || 0) + 1; });

const bookListEl = document.getElementById('book-list');
booksData.forEach(b => {
  const el = document.createElement('div');
  el.className = 'book-item';
  el.dataset.id = b.id;
  el.innerHTML = `<span class="book-dot" style="background:${b.color};color:${b.color}"></span><span class="book-name">${b.name}</span><span class="book-cnt">${bookCounts[b.id] || 0}</span>`;
  el.addEventListener('click', () => {
    if (activeBooks.has(b.id)) { activeBooks.delete(b.id); el.classList.add('off'); }
    else { activeBooks.add(b.id); el.classList.remove('off'); }
    renderGraph();
  });
  bookListEl.appendChild(el);
});

document.getElementById('b-all').addEventListener('click', () => {
  booksData.forEach(b => activeBooks.add(b.id));
  document.querySelectorAll('.book-item').forEach(el => el.classList.remove('off'));
  renderGraph();
});
document.getElementById('b-none').addEventListener('click', () => {
  activeBooks.clear();
  document.querySelectorAll('.book-item').forEach(el => el.classList.add('off'));
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

with open(OUTPUT_PATH, "w") as f:
    f.write(html)

print(f"Generated: {OUTPUT_PATH}")
print(f"  {len(d3_nodes)} nodes, {len(d3_edges)} edges")
print(f"  Open in browser or deploy to GitHub Pages")
