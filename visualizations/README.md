# Knowledge Funnel Visualizations

Interactive D3.js visualizations for chemistry prerequisite exploration.

---

## Files

| File | Description |
|------|-------------|
| `index.html` | Landing page with examples and instructions |
| `scales.html` | Horizontal scale bands visualization |
| `hierarchy.html` | Radial/tree prerequisite hierarchy |

---

## Access

**Requires server running:**

```bash
cd /storage/inorganic-chem-class/infrastructure
source /storage/RAG/.venv/bin/activate
python api_server.py --port 8361
```

**URLs:**

| View | URL |
|------|-----|
| Landing | http://localhost:8361/visualizations/ |
| Scales | http://localhost:8361/visualizations/scales.html |
| Hierarchy | http://localhost:8361/visualizations/hierarchy.html |
| Funnel | http://localhost:8361/funnel.html |

---

## Scale View (`scales.html`)

Concepts arranged in horizontal bands by knowledge scale.

**Features:**
- Strong Y-force keeps nodes in scale bands
- QUANTUM (red) at bottom → DESCRIPTIVE (green) at top
- Click node to re-trace
- Hover for tooltips
- Drag to reposition

**Query parameter:**
```
scales.html?q=crystal%20field%20theory
```

---

## Hierarchy View (`hierarchy.html`)

Radial or tree layout showing prerequisite depth.

**Features:**
- Radial: Target at center, prerequisites expand outward
- Tree: Target at top, prerequisites flow down
- Toggle button to switch layouts
- Depth rings show distance from target
- Click to set new target

**Query parameter:**
```
hierarchy.html?q=molecular%20orbital%20theory
```

---

## Technology

- **D3.js v7** - Force simulation, zoom, drag
- **Vanilla JS** - No frameworks
- **CSS3** - Gradients, animations, responsive
- **Font:** JetBrains Mono

---

## Color Scheme

```css
QUANTUM:     #ef4444 (red)
ELECTRONIC:  #8b5cf6 (purple)
STRUCTURAL:  #06b6d4 (cyan)
DESCRIPTIVE: #22c55e (green)
```

---

## API Dependency

All visualizations fetch from:

```
GET /api/trace?q=<question>
```

Response includes:
- `target` - matched concept
- `all_nodes` - node data with scale, depth, count
- `all_edges` - prerequisite relationships
- `layers` - nodes grouped by scale

---

## Customization

### Change max depth

In each HTML file, modify the fetch URL:

```javascript
// default is 5 levels
fetch(`/api/trace?q=${q}&max_depth=7`)
```

### Change force simulation

Adjust D3 force parameters:

```javascript
simulation
    .force('charge', d3.forceManyBody().strength(-300))  // repulsion
    .force('link', d3.forceLink().distance(80))          // edge length
```

### Change colors

Update the `scaleColors` object:

```javascript
const scaleColors = {
    'QUANTUM': '#ff0000',
    'ELECTRONIC': '#9900ff',
    'STRUCTURAL': '#00cccc',
    'DESCRIPTIVE': '#00cc00'
};
```

---

## Adding New Views

1. Copy an existing HTML file
2. Modify the D3 layout/forces
3. Add link to `index.html`
4. Server automatically serves new files

---

*Part of the CHEM 361 Knowledge Graph Pedagogy Project*
