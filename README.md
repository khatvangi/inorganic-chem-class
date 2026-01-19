# CHEM 361: Inorganic Chemistry - Knowledge Graph Pedagogy

**Interactive learning platform with question-driven prerequisite visualization**

---

## Quick Start

```bash
# 1. start the server
cd /storage/inorganic-chem-class/infrastructure
source /storage/RAG/.venv/bin/activate
python api_server.py --port 8361

# 2. open browser
# http://localhost:8361/visualizations/
```

---

## What Is This?

This project transforms chemistry education from **author-ordered** (textbook chapters) to **learner-ordered** (student questions).

**Traditional approach:** Read Chapter 1 → 2 → 3 → ... → answer emerges somewhere in Chapter 21

**Knowledge Funnel approach:** Ask "Why is copper sulfate blue?" → see ALL prerequisites → learn in dependency order

---

## System Components

### 1. Knowledge Funnel (NEW)

Interactive prerequisite visualization for any chemistry question.

| Component | Location | Description |
|-----------|----------|-------------|
| Landing Page | `/visualizations/index.html` | Examples, instructions, links to all views |
| Scale View | `/visualizations/scales.html` | Horizontal bands by knowledge scale |
| Hierarchy View | `/visualizations/hierarchy.html` | Radial/tree showing prerequisite depth |
| Funnel View | `/funnel.html` | Classic funnel visualization |
| API Server | `/infrastructure/api_server.py` | Backend serving all endpoints |
| Path Tracer | `/infrastructure/path_tracer.py` | Core prerequisite algorithm |

**Access:** http://localhost:8361/visualizations/

### 2. Interactive Games

Six game-based drill modules for coordination chemistry:

| Module | File | Topics |
|--------|------|--------|
| Nomenclature Sprint | `index.html` | IUPAC naming for complexes |
| Structures Lab | `coordination.html` | Coordination geometry (CN 2-8) |
| Isomerism Lab | `isomerism.html` | Geometric & optical isomers |
| Bonding + LFT | `bonding.html` | Crystal field, MO theory |
| Reactions Lab | `reactions.html` | Substitution mechanisms |
| Solids Lab | `solids.html` | Unit cells, packing |

### 3. Knowledge Graph

Built from 7 inorganic chemistry textbooks:

| Metric | Value |
|--------|-------|
| Textbook chunks | 8,753 |
| Concepts (nodes) | 5,380 |
| Prerequisite edges | 2,885 |
| Knowledge scales | 4 |

---

## Knowledge Scales

Concepts are classified into 4 hierarchical scales:

| Scale | Color | Description | Examples |
|-------|-------|-------------|----------|
| QUANTUM | Red | Wave functions, orbitals | Atomic orbitals, quantum numbers |
| ELECTRONIC | Purple | Bonding, energy levels | Crystal field theory, MO theory |
| STRUCTURAL | Cyan | Geometry, symmetry | Point groups, coordination geometry |
| DESCRIPTIVE | Green | Properties, trends | Periodic trends, reactivity |

---

## API Reference

### Trace Prerequisites

```bash
GET /api/trace?q=<question>
```

**Example:**
```bash
curl "http://localhost:8361/api/trace?q=Why%20is%20copper%20sulfate%20blue"
```

**Response:**
```json
{
  "target": "Crystal Field Theory",
  "all_nodes": {
    "Crystal Field Theory": {"scale": "ELECTRONIC", "depth": 0},
    "Molecular Orbital Theory": {"scale": "QUANTUM", "depth": 1},
    ...
  },
  "all_edges": [
    {"source": "Molecular Orbital Theory", "target": "Crystal Field Theory"},
    ...
  ],
  "layers": {
    "QUANTUM": ["Molecular Orbital Theory", "Atomic Orbitals", ...],
    "ELECTRONIC": ["Crystal Field Theory", ...],
    ...
  }
}
```

### List Concepts

```bash
GET /api/concepts
```

### Health Check

```bash
GET /api/health
```

---

## Example Questions

| Question | Target Concept | Node Count |
|----------|---------------|------------|
| "Why is copper sulfate blue?" | Crystal Field Theory | ~124 |
| "How do unpaired electrons cause magnetism?" | Magnetic Properties | ~80 |
| "What is molecular orbital theory?" | MO Theory | ~95 |
| "Why does electronegativity increase across a period?" | Periodic Trends | ~60 |

---

## Directory Structure

```
inorganic-chem-class/
├── README.md                    # this file
├── funnel.html                  # classic funnel visualization
├── prototype_novel.html         # demo of novel pedagogy features
│
├── visualizations/
│   ├── index.html               # landing page with examples
│   ├── scales.html              # scale-layered visualization
│   └── hierarchy.html           # radial/tree view
│
├── infrastructure/
│   ├── api_server.py            # HTTP server (port 8361)
│   ├── path_tracer.py           # prerequisite tracing algorithm
│   ├── verify_sources.py        # data verification
│   ├── curriculum_schema.py     # curriculum data structures
│   └── README.md                # infrastructure docs
│
├── docs/
│   ├── KNOWLEDGE_FUNNEL_METHODOLOGY.md  # detailed methodology
│   └── ...                      # other documentation
│
├── data/                        # JSON question banks
├── js/                          # shared JavaScript utilities
├── libs/                        # external libraries (ChemDoodle)
└── lectures/                    # slide decks
```

---

## Data Sources

**Verified textbooks** (8,753 total chunks):

| Textbook | Chunks | % |
|----------|--------|---|
| Atkins/Shriver - Inorganic Chemistry | 2,494 | 28.5% |
| Housecroft/Sharpe - Inorganic Chemistry | 2,375 | 27.1% |
| Douglas/McDaniel - Descriptive IC | 1,495 | 17.1% |
| House - Descriptive IC | 1,027 | 11.7% |
| JD Lee - Concise IC | 565 | 6.5% |
| Basset - IC | 446 | 5.1% |
| Advanced IC Applications | 351 | 4.0% |

---

## Novel Pedagogy Features

### 1. Bridge Explanations

Explicit connections between concepts:

> "You learned **d-orbitals have different shapes**. Now see how this explains **why some orbitals go up in energy**: The eg orbitals point directly at ligands, experiencing more repulsion."

### 2. Scale Zoom

Same phenomenon at 4 depths:

| Scale | Explanation |
|-------|-------------|
| DESCRIPTIVE | "Copper compounds are typically blue or green" |
| STRUCTURAL | "Cu²⁺ forms octahedral [Cu(H₂O)₆]²⁺" |
| ELECTRONIC | "d-d transition absorbs orange (~600nm), transmits blue" |
| QUANTUM | "Laporte-forbidden but vibronically allowed transition" |

### 3. Question-Driven Paths

Instead of "read Chapter 21", the system provides:
1. Prerequisites the student already knows (skip)
2. Prerequisites to learn (ordered by dependency)
3. Target concept
4. Visual map of the entire path

---

## Technology Stack

- **Backend:** Python 3, NetworkX, Qdrant vector database
- **Frontend:** D3.js, vanilla HTML/CSS/JS
- **LLM:** Qwen3 via Ollama (for knowledge extraction)
- **Games:** ChemDoodle Web Components, ES6 modules

---

## Running the Full System

### Prerequisites

```bash
# Qdrant must be running
curl http://localhost:6333/collections

# Python environment
source /storage/RAG/.venv/bin/activate
```

### Start Server

```bash
cd /storage/inorganic-chem-class/infrastructure
python api_server.py --port 8361
```

### Access Points

| URL | Description |
|-----|-------------|
| http://localhost:8361/visualizations/ | Knowledge Funnel landing |
| http://localhost:8361/funnel.html | Classic funnel view |
| http://localhost:8361/index.html | Interactive games |

---

## Documentation

| Document | Description |
|----------|-------------|
| `docs/KNOWLEDGE_FUNNEL_METHODOLOGY.md` | Full methodology, algorithms, results |
| `infrastructure/README.md` | Infrastructure for all chemistry subfields |
| `infrastructure/NOVEL_PEDAGOGY.md` | Novel pedagogical features |
| `QUICKSTART.md` | Quick start guide |

---

## Future Work

- [ ] Student tracking (mastered concepts)
- [ ] Adaptive paths (skip known prerequisites)
- [ ] Quiz integration at each node
- [ ] Extend to organic, physical, analytical chemistry
- [ ] Integration with chem361.thebeakers.com

---

## Authors

- **Kiran Brahma** - Course design, pedagogy
- **Claude** - AI Assistant, implementation

---

*CHEM 361 Inorganic Chemistry | Knowledge Graph Pedagogy Project | 2026*
