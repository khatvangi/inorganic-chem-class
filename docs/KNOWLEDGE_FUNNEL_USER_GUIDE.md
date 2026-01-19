# Knowledge Funnel - User Guide

**Interactive prerequisite visualization for chemistry learning**

---

## Getting Started

### 1. Start the Server

```bash
cd /storage/inorganic-chem-class/infrastructure
source /storage/RAG/.venv/bin/activate
python api_server.py --port 8361
```

### 2. Open the Landing Page

Navigate to: **http://localhost:8361/visualizations/**

---

## Three Visualization Views

### Scale View (`scales.html`)

**Best for:** Seeing how concepts relate across knowledge levels

- Concepts arranged in **horizontal bands** by scale
- QUANTUM at bottom → DESCRIPTIVE at top
- Nodes float within their scale band
- Strong visual separation between levels

**How to use:**
1. Enter a question in the search box
2. See concepts organized by scale
3. Click any node to re-trace from that concept
4. Drag nodes to rearrange
5. Hover for details

---

### Hierarchy View (`hierarchy.html`)

**Best for:** Understanding prerequisite depth and chains

- **Radial layout:** Target at center, prerequisites expand outward
- **Tree layout:** Target at top, prerequisites flow down
- Depth rings show distance from target
- Toggle between layouts with the button

**How to use:**
1. Enter a question
2. Target appears at center/top
3. Direct prerequisites are closest
4. Deeper prerequisites extend outward/downward
5. Click node to make it the new target

---

### Funnel View (`funnel.html`)

**Best for:** Overview of the learning path

- Classic force-directed graph
- Y-position loosely follows scale
- Glow effect on highlighted nodes
- Most flexible layout

**How to use:**
1. Enter a question
2. Explore the force-directed layout
3. Drag nodes to organize
4. Zoom and pan to navigate

---

## Understanding the Colors

| Color | Scale | What It Contains |
|-------|-------|------------------|
| Red | QUANTUM | Wave functions, orbitals, quantum numbers |
| Purple | ELECTRONIC | Crystal field theory, MO theory, bonding |
| Cyan | STRUCTURAL | Point groups, geometry, symmetry |
| Green | DESCRIPTIVE | Periodic trends, properties, reactions |

---

## Example Questions to Try

### Color & Spectroscopy
```
Why is copper sulfate blue?
```
→ Traces through Crystal Field Theory, d-d transitions, orbital splitting

### Magnetism
```
How do unpaired electrons cause magnetism?
```
→ Shows spin states, electron configuration, orbital occupancy

### Bonding Theory
```
What is molecular orbital theory?
```
→ Reveals atomic orbitals, bonding/antibonding, MO diagrams

### Symmetry
```
How do point groups relate to spectroscopy?
```
→ Connects symmetry operations to selection rules

### Periodic Trends
```
Why does electronegativity increase across a period?
```
→ Shows effective nuclear charge, shielding, atomic structure

---

## Interacting with Nodes

### Click
- Re-traces prerequisites from that concept
- Makes the clicked node the new target
- Updates the entire visualization

### Hover
- Shows node details
- Displays concept name, scale, mention count
- Highlights connected edges

### Drag
- Repositions the node
- Useful for organizing the view
- Other nodes adjust via force simulation

---

## Reading the Path

### From Bottom to Top

1. **Start at QUANTUM (bottom/outside)**
   - These are the fundamental concepts
   - Learn these first

2. **Move to ELECTRONIC**
   - Builds on quantum foundations
   - Explains bonding and energy

3. **Continue to STRUCTURAL**
   - Uses electronic concepts
   - Explains geometry and symmetry

4. **Arrive at DESCRIPTIVE (top/center)**
   - The answer to your question
   - Requires understanding of lower levels

### Edge Direction

Arrows point from **prerequisite → dependent concept**

```
Atomic Orbitals → Molecular Orbital Theory → Crystal Field Theory
```

This means:
- You need Atomic Orbitals to understand MO Theory
- You need MO Theory to understand Crystal Field Theory

---

## API Usage

### From Command Line

```bash
# trace prerequisites
curl "http://localhost:8361/api/trace?q=Why%20is%20copper%20sulfate%20blue"

# list all concepts
curl "http://localhost:8361/api/concepts"

# health check
curl "http://localhost:8361/api/health"
```

### From JavaScript

```javascript
async function traceQuestion(question) {
    const response = await fetch(`/api/trace?q=${encodeURIComponent(question)}`);
    const data = await response.json();

    console.log('Target:', data.target);
    console.log('Nodes:', Object.keys(data.all_nodes).length);
    console.log('Edges:', data.all_edges.length);
    console.log('Layers:', data.layers);
}
```

### Response Structure

```json
{
  "target": "Crystal Field Theory",
  "target_info": {
    "label": "Crystal Field Theory",
    "type": "topic",
    "count": 165,
    "scale": "ELECTRONIC",
    "pagerank": 0.00166
  },
  "all_nodes": {
    "Concept Name": {
      "id": "Concept Name",
      "scale": "QUANTUM|ELECTRONIC|STRUCTURAL|DESCRIPTIVE",
      "depth": 0,
      "count": 42,
      "pagerank": 0.00123,
      "is_target": false
    }
  },
  "all_edges": [
    {"source": "Prerequisite", "target": "Dependent Concept"}
  ],
  "layers": {
    "QUANTUM": ["Concept1", "Concept2"],
    "ELECTRONIC": ["Concept3"],
    "STRUCTURAL": ["Concept4"],
    "DESCRIPTIVE": ["Concept5"]
  }
}
```

---

## Tips for Effective Use

### 1. Start with Your Real Question

Don't think about what chapter to read. Ask what you actually want to know.

### 2. Follow the Funnel Down

Your question is at the narrow end. Follow prerequisites down to the wide foundation.

### 3. Identify Gaps

If you don't understand a node, that's where to study next.

### 4. Use Multiple Views

- **Scale View** for understanding levels
- **Hierarchy View** for depth
- **Funnel View** for overall structure

### 5. Click to Dive Deeper

Any concept can become the new target. Click to explore its prerequisites.

---

## Troubleshooting

### "No results found"

The question may not match any concepts. Try:
- Using chemistry terminology
- Asking about a specific concept
- Checking spelling

### Visualization is slow

Large graphs (100+ nodes) may lag. Try:
- Zooming to focus on a region
- Clicking a specific node to trace a smaller subgraph

### Server not responding

```bash
# check if server is running
pgrep -f api_server.py

# restart if needed
python api_server.py --port 8361
```

### Qdrant not running

```bash
# check Qdrant
curl http://localhost:6333/collections

# the server will still work but may have limited data
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Enter | Submit question |
| Scroll | Zoom in/out |
| Click + Drag | Pan view |
| Double-click | Reset zoom |

---

*Knowledge Funnel - Transforming chemistry education from author-ordered to learner-ordered*
