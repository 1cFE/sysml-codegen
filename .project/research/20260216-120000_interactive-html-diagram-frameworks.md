---
date: 2026-02-16T12:00:00-05:00
researcher: Claude
topic: "Interactive HTML diagram frameworks for algorithm documentation"
tags: [research, visualization, tooling, documentation, claude-skill]
status: complete
last_updated: 2026-02-16
---

# Research: Interactive HTML Diagram Frameworks for Algorithm Documentation

**Date**: 2026-02-16
**Researcher**: Claude
**Research Type**: Tooling / Domain

## Research Question

The current algorithm documentation (`08_algorithm_revised.md`, `08_block_diagrams.md`)
uses ASCII art and linear markdown. This is hard for new users to approach. The ideal
is an HTML-based diagram where explanatory text and source code references appear as
tooltips on hover/click. This should be AI-generatable (Claude skill candidate) and
produce self-contained HTML files.

## Summary

- **Vanilla HTML + inline SVG + vanilla JS** is the strongest candidate: Claude excels at generating self-contained HTML artifacts, tooltips are trivial with native SVG `<title>` or CSS/JS popovers, zero dependencies, and the output is a single `.html` file
- **Mermaid.js (CDN)** is a strong runner-up for simpler diagrams: text-based DSL that Claude can generate, built-in tooltip support, but limited interactivity and layout control
- **ELK.js + vanilla SVG** is the best option for complex DAG/pipeline layouts: automatic hierarchical layout avoids manual coordinate math, but adds ~300KB dependency
- **D3.js** is powerful but its learning curve makes it a poor fit for a Claude skill where the LLM needs to reliably generate correct code on each invocation
- **Commercial frameworks** (GoJS, JointJS) are overkill and add licensing constraints

## Detailed Findings

### Approach 1: Vanilla HTML + SVG + Inline JavaScript (RECOMMENDED)

**What it is:** A single self-contained `.html` file with inline SVG graphics and
vanilla JavaScript for interactivity. No external dependencies.

**Why it fits:**
- Claude is already proven at generating self-contained HTML/SVG artifacts (this is
  the core Claude Artifacts pattern from claude.ai)
- Anthropic's own documentation showcases this: [Build interactive diagram tools](https://claude.com/resources/use-cases/build-interactive-diagram-tools)
- Tooltips are straightforward: either SVG `<title>` elements (browser-native), CSS
  `:hover` + `::after` pseudo-elements, or a small JS tooltip handler
- Source code references can be embedded as `data-*` attributes on SVG elements
- The output is a single file you can open in any browser, email, or commit to git
- No build step, no node_modules, no framework lock-in

**Tooltip patterns (three levels of sophistication):**

```html
<!-- Level 1: Native SVG title (browser tooltip, no JS needed) -->
<rect class="step" x="10" y="10" width="200" height="60">
  <title>Step 1: Load Models
IMPL: extraction/extractor.py :: SysMLDataExtractor.load_models() (:51)
Parses .sysml files via SysIDE adapter into in-memory AST.</title>
</rect>

<!-- Level 2: CSS hover tooltip (styled, no JS) -->
<g class="node" data-tooltip="...">
  <rect .../>
  <text>Step 1</text>
</g>
<style>
  .node:hover .tooltip-text { opacity: 1; }
</style>

<!-- Level 3: JS popover (rich HTML content, positioning control) -->
<g class="node"
   data-impl="extraction/extractor.py:51"
   data-desc="Parses .sysml files via SysIDE adapter"
   onmouseenter="showTooltip(event, this)"
   onmouseleave="hideTooltip()">
</g>
```

**Strengths:**
- Maximum control over layout, styling, and interaction
- Claude can generate the entire file in one shot
- Easy to iterate: "move this box to the right", "add a tooltip to X"
- Works offline, no CDN dependency
- Git-diffable (text-based)

**Weaknesses:**
- Manual coordinate math for positioning nodes and edges
- No automatic layout (you specify x/y for everything)
- Complex diagrams (20+ nodes) require careful spatial planning

**AI-friendliness: HIGH** - This is Claude's strongest generation mode.

---

### Approach 2: Mermaid.js (via CDN)

**What it is:** A text-based diagramming DSL that renders to SVG. Load via CDN script
tag, write diagram definitions as text, Mermaid renders them.

**Why it fits:**
- Text-based input is natural for LLM generation
- Built-in tooltip support: `click A callback "Tooltip text"`
- Automatic layout (dagre-based internally)
- Single HTML file with one `<script>` CDN tag

**Tooltip syntax:**
```
graph TD
    A[Step 1: Load Models]
    click A callback "IMPL: extraction/extractor.py:51"
```

**Post-render tooltip injection (more flexible):**
```javascript
// After Mermaid renders, bind rich tooltips to nodes
const svg = document.querySelector('.mermaid svg');
svg.querySelectorAll('.node').forEach(node => {
  const id = node.id;
  const data = tooltipData[id]; // your tooltip content map
  node.addEventListener('mouseenter', (e) => showRichTooltip(e, data));
});
```

**Strengths:**
- Automatic layout eliminates coordinate math
- Familiar syntax (used in GitHub, GitLab, Notion)
- Claude already knows Mermaid syntax well
- Good for flowcharts, sequence diagrams, class diagrams

**Weaknesses:**
- Limited styling control (Mermaid's CSS is opaque)
- Tooltip support is basic (text only, no rich HTML tooltips natively)
- Complex diagrams with many nodes can produce poor layouts
- The ASCII-art-style diagrams in `08_block_diagrams.md` are **not** standard
  flowcharts -- they're box-and-arrow diagrams with nested content, data model
  listings, and multi-line annotations. Mermaid can't represent this richness.
- Click callbacks require `securityLevel: 'loose'` (XSS consideration)

**AI-friendliness: HIGH** for simple diagrams, MEDIUM for complex ones.

---

### Approach 3: ELK.js Layout + Vanilla SVG Rendering

**What it is:** ELK.js computes node positions using professional graph layout
algorithms (the Eclipse Layout Kernel, ported to JS). You define graph structure
as JSON, ELK computes coordinates, then you render with vanilla SVG.

**Why it fits:**
- Hierarchical layout algorithm is ideal for pipeline DAGs
- Handles complex graphs (20-50+ nodes) with good results
- Separation of concerns: data model (JSON) -> layout (ELK) -> rendering (SVG)
- ~300KB library, can be loaded via CDN

**Pattern:**
```javascript
const elk = new ELK();
const graph = {
  id: "root",
  layoutOptions: { 'elk.algorithm': 'layered' },
  children: [
    { id: "step1", width: 200, height: 60,
      labels: [{ text: "Step 1: Load Models" }] },
    { id: "step2", width: 200, height: 60,
      labels: [{ text: "Step 2: Extract CalcDefs" }] },
  ],
  edges: [
    { id: "e1", sources: ["step1"], targets: ["step2"] }
  ]
};

elk.layout(graph).then(layoutedGraph => {
  // Render to SVG using computed x, y coordinates
  renderToSVG(layoutedGraph);
});
```

**Strengths:**
- Professional-quality automatic layout for DAGs and hierarchies
- Highly configurable (hundreds of layout options)
- Solves the biggest pain point of Approach 1 (manual coordinates)
- Still outputs to vanilla SVG (tooltips work the same way)
- Actively maintained (unlike dagre which is deprecated)

**Weaknesses:**
- ~300KB library dependency (CDN or bundled)
- More complex generation template for Claude
- Layout is async (uses Promises)
- Documentation is dense (Java-heritage library)

**AI-friendliness: MEDIUM** - The JSON graph definition is straightforward for
Claude to generate, but the rendering boilerplate is significant. Best addressed
with a reusable template/harness.

---

### Approach 4: D3.js

**What it is:** The gold standard data visualization library. Bindsd data to DOM
elements with enter/update/exit patterns.

**Why it fits:**
- Extremely powerful for custom visualizations
- Rich tooltip ecosystem (d3-tip, native implementations)
- Can handle any diagram type
- Huge community and documentation

**Weaknesses:**
- Steep learning curve -- D3's idioms are unique and error-prone
- Claude often generates subtly broken D3 code (wrong selection patterns, missing
  data joins) because the API is stateful and order-dependent
- Overkill for what is essentially "boxes with arrows and tooltips"
- No automatic graph layout built-in (need dagre or elk separately)

**AI-friendliness: LOW** - D3's declarative-imperative hybrid style produces
unreliable LLM output. Frequent debugging needed.

---

### Approach 5: Cytoscape.js

**What it is:** Graph theory visualization library. Strong for network graphs.

**Why it fits:**
- Built-in layout algorithms (cola, dagre, klay, etc.)
- Event system for hover/click interactions
- Tooltip via extensions (cytoscape-popper, tippy.js integration)

**Weaknesses:**
- Optimized for network/graph visualization, not structured box diagrams
- Node content is limited (no rich multi-line text inside nodes)
- Extension ecosystem adds dependency complexity
- The diagrams in `08_block_diagrams.md` are not graph-theory graphs -- they're
  structured documentation with nested boxes, field listings, and annotations

**AI-friendliness: MEDIUM** - API is clean but extension configuration is finicky.

---

### Approach 6: Commercial (GoJS, JointJS)

**GoJS:** Feature-rich, built-in tooltips and context menus. But commercial
license required (~$7K+). Excellent quality but unnecessary for internal docs.

**JointJS:** Open-source core, commercial JointJS+ for advanced features.
Tooltip support via JointJS+ (commercial). Clean API but heavy.

**AI-friendliness: MEDIUM** - Good APIs but license and bundle size overhead.

---

## Feasibility Assessment for Claude Skill

### The Skill Architecture

A Claude diagramming skill would need:

1. **Input:** A markdown document (like `08_block_diagrams.md`) or a structured
   description of the diagram content
2. **Output:** A self-contained `.html` file with interactive SVG diagrams
3. **Template:** A reusable HTML/JS harness that Claude fills in with diagram data

### Recommended Architecture: ELK.js + Vanilla SVG (with template)

```
User invokes skill with markdown input
    |
    v
Claude parses the conceptual diagram structure
    |
    v
Claude generates a JSON graph definition (nodes, edges, tooltips)
    |
    v
Template harness (pre-built HTML/JS):
  - Loads ELK.js from CDN
  - Runs layout on the JSON graph
  - Renders SVG with styled nodes and edges
  - Attaches tooltip handlers using data from the JSON
    |
    v
Single .html file output
```

**Why this architecture:**
- Claude only needs to generate the **graph JSON** (its strength), not pixel-perfect
  SVG coordinates (its weakness)
- The template harness handles rendering, tooltips, and styling consistently
- ELK.js handles layout automatically
- The harness can be versioned and improved independently of the skill prompt

### Alternative: Pure Vanilla SVG (for simpler diagrams)

For diagrams with < 10 nodes (like decision trees, small flowcharts), skip ELK.js
and have Claude generate the SVG directly. Claude handles small SVGs well.

### Hybrid Approach (Best of Both)

- **Simple diagrams** (decision trees, small flows): Vanilla HTML+SVG, no dependencies
- **Complex DAGs** (full pipeline, OutputRegistry phases): ELK.js + template harness
- **Quick documentation** (class diagrams, simple sequences): Mermaid.js

The skill could auto-select based on diagram complexity.

## Specific Fit for Current Diagrams

| Diagram in 08_block_diagrams.md | Best Approach | Reasoning |
|---|---|---|
| 1. Full Pipeline Data Flow | ELK.js + template | 8 major stages, nested data models, many edges |
| 2. OutputRegistry Phases | ELK.js + template | 4 phases with internal detail, cross-phase resolution arrows |
| 3. Binding Resolution Decision Tree | Vanilla SVG | Tree structure, ~15 nodes, straightforward |
| 4. Three Module Families | ELK.js + template | Complex nested boxes with field listings |
| 5. Template Expansion | Vanilla SVG | Small, focused diagram |
| 6. End-to-End Wiring Example | ELK.js + template | Multi-family cross-wiring, aliases |
| 7. Naming System Quick Reference | Vanilla SVG | Small tree, few nodes |
| 8. Computed Attribute Classification | Vanilla SVG | Decision tree, ~12 nodes |

## Recommendations

### Immediate Action: Prototype with Vanilla SVG

Pick diagram #3 (Binding Resolution Decision Tree) or #8 (Computed Attribute
Classification) -- both are small decision trees. Have Claude generate a
self-contained HTML file with:
- SVG boxes for each decision node
- Arrows connecting them
- Hover tooltips showing IMPL references and descriptions
- Click-to-highlight for tracing paths

This validates the concept with minimal investment.

### Short-term: Build ELK.js Template Harness

Create a reusable `diagram-harness.html` template that:
1. Loads ELK.js from CDN (`https://cdn.jsdelivr.net/npm/elkjs/lib/elk.bundled.js`)
2. Accepts a `DIAGRAM_DATA` JSON variable defining nodes, edges, and tooltip content
3. Runs ELK layout, renders SVG, attaches tooltips
4. Includes a consistent style (colors, fonts, hover effects)

Then the Claude skill only needs to generate the JSON data, not the rendering code.

### Medium-term: Claude Skill Design

```yaml
# Proposed skill structure
name: diagram
trigger: "/_my_diagram"
input: markdown file path or inline description
output: .project/diagrams/{name}.html

# Skill would:
# 1. Read the source markdown/description
# 2. Analyze diagram complexity
# 3. Choose approach (vanilla SVG vs ELK.js)
# 4. Generate the appropriate HTML file
# 5. Report the output path
```

### Things to Avoid

- **Don't use React/Vue/Angular** -- framework lock-in for documentation files is wrong
- **Don't use D3.js** -- unreliable LLM generation, overkill for this use case
- **Don't invest in commercial libraries** -- the free options fully cover this need
- **Don't try to make Mermaid do everything** -- it's great for simple diagrams but
  can't handle the richness of the `08_block_diagrams.md` content (nested boxes,
  multi-line field listings, cross-references)

## Open Questions

1. **Tooltip richness:** Should tooltips contain just text, or also code snippets
   with syntax highlighting? (Adds complexity but significantly improves usability)
2. **Navigation:** Should clicking a source reference open the file in VS Code
   (via `vscode://file/...` URI scheme)? This would make the diagrams truly
   integrated with the dev workflow.
3. **Dark mode:** Should the diagrams support light/dark themes?
4. **Export:** Should the HTML also embed a "print-friendly" CSS media query for
   generating PDFs?

## Sources

- [Build interactive diagram tools | Claude](https://claude.com/resources/use-cases/build-interactive-diagram-tools)
- [GoJS - Interactive Diagrams for the Web](https://gojs.net/latest/)
- [Top 8 JavaScript diagramming libraries in 2026](https://www.jointjs.com/blog/javascript-diagramming-libraries)
- [JointJS - JavaScript diagramming library](https://www.jointjs.com)
- [D3 Graph Gallery - Tooltips](https://d3-graph-gallery.com/graph/interactivity_tooltip.html)
- [Mermaid Flowchart Syntax](https://mermaid.js.org/syntax/flowchart.html)
- [ELK.js - Layout algorithms for JavaScript](https://github.com/kieler/elkjs)
- [Eclipse Layout Kernel](https://eclipse.dev/elk/)
- [React Flow - ELK.js Example](https://reactflow.dev/examples/layout/elkjs)
- [Adding interactive tooltips to SVG files](https://www.carlos-toruno.com/blog/svg-tooltips/)
- [SVG Interactive Tooltip Tutorial](https://www.petercollingridge.co.uk/tutorials/svg/interactive/tooltip/)
- [20+ JavaScript libraries for diagrams](https://modeling-languages.com/javascript-drawing-libraries-diagrams/)
- [Cytoscape vs vis-network vs dagre-d3 comparison](https://npm-compare.com/cytoscape,d3-graphviz,dagre-d3,gojs,vis-network)
- [Mermaid Modal Popup pattern](https://paultraylor.net/blog/2025/mermaid-modal-popup/)
- [Tippy.js - Tooltip and Popover Library](https://atomiks.github.io/tippyjs/)
