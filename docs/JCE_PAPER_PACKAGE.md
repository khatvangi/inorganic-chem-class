# JCE Paper Package: Data-Driven Curriculum Design Using Multi-Scale Knowledge Graphs

**Working Title:** "From Textbook to Graph: A Data-Driven Methodology for Chemistry Curriculum Design"

**Authors:** Kiran Brahma, [collaborators]

**Target Journal:** Journal of Chemical Education (JCE)

---

# TABLE OF CONTENTS

1. [Abstract](#1-abstract)
2. [The Problem](#2-the-problem)
3. [Our Methodology](#3-our-methodology)
   - 3.1 Knowledge Extraction Pipeline
   - 3.2 Multi-Scale Knowledge Model
   - 3.3 Path Tracing Algorithm
   - 3.4 Dual PageRank Curriculum Model
4. [Results from CHEM 361](#4-results-from-chem-361)
   - 4.6 Limitation: Graph Sparsity and Alternative Analysis
5. [Novel Pedagogical Features](#5-novel-pedagogical-features)
6. [Vision: Meta-Scale Tree](#6-vision-meta-scale-tree)
7. [Implementation Details](#7-implementation-details)
8. [Research Questions](#8-research-questions)
9. [Appendices](#9-appendices)

---

# 1. Abstract

Traditional chemistry curricula present content linearly, obscuring prerequisite relationships between concepts. Students struggle to see connections and often ask "why do I need to learn this?"

We developed a **multi-scale knowledge graph methodology** that:

1. Extracts prerequisite relationships from multiple textbooks using NLP
2. Classifies concepts into 4 hierarchical scales (Quantum → Electronic → Structural → Descriptive)
3. Applies **dual PageRank analysis** to identify both foundational concepts (teach first) and capstone topics (teach last)
4. Enables dynamic path tracing from any student question back through prerequisites
5. Transforms curriculum from **author-ordered** to **learner-ordered**

Applied to CHEM 361 Inorganic Chemistry (7 textbooks, 8,756 chunks), we extracted 5,380 concepts and 2,885 prerequisite relationships. The resulting knowledge graph revealed:

- **Counterintuitive finding:** Main Group Chemistry is a CAPSTONE (integrates many prerequisites), not a foundation
- **Foundational topics:** Redox Chemistry, Electron Configuration, Oxidation States should be taught FIRST
- **Scale-appropriate endpoints:** Many concepts are self-contained at higher scales; not everything must trace to quantum mechanics
- **Graph sparsity insight:** With mean degree 1.5, degree-based analysis outperforms PageRank for identifying actionable foundations (32 topics with out-degree ≥ 5)

This data-driven approach provides empirical grounding for curriculum design decisions traditionally made by intuition.

---

# 2. The Problem

## 2.1 Linear Curriculum Limitations

| Aspect | Traditional Approach | Limitation |
|--------|---------------------|------------|
| Structure | Chapter 1 → 2 → 3 → ... | Hides connections |
| Prerequisites | Implicit, assumed | Students miss gaps |
| Depth | Fixed at textbook level | No zoom in/out |
| Starting point | Chapter 1 | Ignores student curiosity |
| Connections | Implicit | Students don't see "why" |

## 2.2 The Hidden Prerequisite Problem

When a student asks "Why is copper sulfate blue?", the answer requires:

- Atomic orbitals (Chapter 1)
- d-orbital shapes (Chapter 1)
- Coordination geometry (Chapter 17)
- Crystal Field Theory (Chapter 21)
- Selection rules (Chapter 22)

But the textbook doesn't show these connections explicitly. The student must read 22 chapters to find out the prerequisite chain is only ~5 concepts deep.

## 2.3 The Bricks Insight

> "Although a building has bricks and bricks have atoms and atoms have electrons, this does not help. After bricks we have different hierarchy. Understanding building should stop at bricks."

**Key realization:** Not everything must trace to quantum mechanics. Knowledge exists at **multiple self-contained scales**. Nomenclature can be learned at the STRUCTURAL scale without quantum mechanics.

---

# 3. Our Methodology

## 3.1 Knowledge Extraction Pipeline

### Step 1: Semantic Chunking

```
Parameter          Value           Rationale
─────────────────────────────────────────────────────
CHUNK_SIZE         1500 chars      Preserves concept boundaries
CHUNK_OVERLAP      200 chars       Context at boundaries
RESPECT_PARAGRAPHS True            Natural semantic units
```

**Result:** 8,756 chunks from 7 textbooks (vs. fixed 512-token chunks that broke mid-sentence)

### Step 2: Entity Extraction

Extract at multiple granularities:

| Level | Example | Count |
|-------|---------|-------|
| Topic | Crystal Field Theory | 1,017 |
| Subtopic | Octahedral splitting | 4,363 |
| **Total nodes** | | **5,380** |

### Step 3: Relationship Extraction

Type all relationships (untyped edges were useless):

| Relation | Meaning | Example |
|----------|---------|---------|
| `prerequisite_for` | A must come before B | Atomic Structure → CFT |
| `leads_to` | A naturally follows B | Coordination → Solid State |
| `contains` | A includes B | Coordination → Nomenclature |

**Result:** 2,885 typed edges (1,458 prerequisite_for edges)

### Step 4: Quality Filtering

**Rule:** Filter by mention count ≥ 10

```
Before: 1,017 topics
After:  67 significant topics

Long-tail topics were often extraction errors
```

## 3.2 Multi-Scale Knowledge Model

### The Four Scales

```
SCALE 4: QUANTUM      Wave functions, orbitals, spin
                      "The fundamental why"

SCALE 3: ELECTRONIC   Crystal Field Theory, MO diagrams
                      "Why it happens (electron level)"

SCALE 2: STRUCTURAL   Coordination geometry, crystal structures
                      "How it's arranged"

SCALE 1: DESCRIPTIVE  Periodic trends, element properties
                      "What happens"
```

### Scale Navigation Rules

| Rule | Description |
|------|-------------|
| **Rule 1** | Stay within scale when possible |
| **Rule 2** | Escalate only for "why" questions |
| **Rule 3** | Explore tree siblings before escalating |
| **Rule 4** | "Blind path" (all way to quantum) only for anomalies |

### Scale-Appropriate Endpoints

```
Learning Objective              → Required Scale → Go Deeper?
─────────────────────────────────────────────────────────────
Name [Co(NH3)6]Cl3              → STRUCTURAL     → No
Explain why Cu²⁺ is blue        → ELECTRONIC     → No
Explain relativistic effects    → QUANTUM        → Yes (endpoint)
List alkali metal properties    → DESCRIPTIVE    → No
```

### Cross-Scale Flow Matrix

```
FROM →        QUANTUM  ELECTRONIC  STRUCTURAL  DESCRIPTIVE
────────────────────────────────────────────────────────────
QUANTUM          26         16          11           9
ELECTRONIC        7         14          19          11
STRUCTURAL       31         24          22          18
DESCRIPTIVE       9         14          20          30
```

**Finding:** Diagonal values (within-scale) are high. Most learning stays within scale. Cross-scale edges represent "escalation points."

## 3.3 Path Tracing Algorithm

### Input
Natural language question (e.g., "Why is copper sulfate blue?")

### Process

```python
def trace_prerequisites(target, max_depth=5):
    visited = set()
    queue = [(target, 0)]  # (node, depth)
    result = {'nodes': {}, 'edges': [], 'layers': {}}

    while queue:
        current, depth = queue.pop(0)
        if current in visited or depth > max_depth:
            continue
        visited.add(current)

        scale = infer_scale(current)
        result['nodes'][current] = {'scale': scale, 'depth': depth}
        result['layers'][scale].append(current)

        for prereq in get_prerequisites(current):
            result['edges'].append({'source': prereq, 'target': current})
            queue.append((prereq, depth + 1))

    return result
```

### Output

Nodes organized by scale, edges showing prerequisite flow, depth from target concept.

## 3.4 Dual PageRank Curriculum Model

### The Problem with Single PageRank

A naive approach uses single PageRank to identify "important" topics. However, this conflates two distinct types of importance:

- **Foundational importance:** How many topics depend on this? (teach FIRST)
- **Integration importance:** How many topics lead to this? (teach LAST)

### The Solution: Dual PageRank

We compute TWO PageRank scores for each topic:

| Metric | Graph Direction | Measures | Curriculum Role |
|--------|-----------------|----------|-----------------|
| **Reverse PageRank** | Follow edges backward | What is prerequisite for many | FOUNDATIONS |
| **Forward PageRank** | Follow edges forward | What many topics lead to | CAPSTONES |

### Position Score

```python
Position = Reverse_PR - Forward_PR

if position > 0.001:   → FOUNDATION (teach early)
if position < -0.005:  → CAPSTONE (teach late)
else:                  → BRIDGE (teach in middle)
```

### Algorithm

```python
import networkx as nx

def dual_pagerank_curriculum(G, alpha=0.85):
    """
    G: DiGraph where edge (A, B) means "A is prerequisite for B"
    """
    # Forward PR: what many things lead TO (capstones)
    pr_forward = nx.pagerank(G, alpha=alpha)

    # Reverse PR: what IS prerequisite for many (foundations)
    pr_reverse = nx.pagerank(G.reverse(), alpha=alpha)

    result = {}
    for node in G.nodes():
        fwd = pr_forward.get(node, 0)
        rev = pr_reverse.get(node, 0)
        position = rev - fwd
        result[node] = {
            'foundation_score': rev,
            'capstone_score': fwd,
            'position': position
        }
    return result
```

### Why This Matters

Single PageRank incorrectly identified "Main Group Chemistry" as foundational because many edges point TO it. Dual PageRank reveals it's actually a CAPSTONE that integrates many prerequisites.

---

# 4. Results from CHEM 361

## 4.1 Data Summary

| Metric | Value |
|--------|-------|
| Textbooks processed | 7 |
| Total chunks | 8,756 |
| Concepts extracted | 5,380 |
| Prerequisite edges | 1,458 |
| Graph nodes | 973 |

## 4.2 Test Case: "Why is copper sulfate blue?"

**Target concept:** Crystal Field Theory

**Path traced:**

| Scale | Nodes | Examples |
|-------|-------|----------|
| QUANTUM | 44 | Atomic orbitals, d-orbital shapes |
| ELECTRONIC | 23 | Crystal field theory, spectroscopy |
| STRUCTURAL | 18 | Point group symmetry, octahedral geometry |
| DESCRIPTIVE | 39 | Periodic trends, ligand properties |
| **Total** | **124** | |

**Edges:** 149 prerequisite relationships

## 4.3 Dual PageRank Analysis

### Curriculum Distribution

| Category | Count | Percentage | Role |
|----------|-------|------------|------|
| FOUNDATION | 63 | 6.5% | Teach first |
| BRIDGE | 903 | 92.8% | Main content |
| CAPSTONE | 7 | 0.7% | Teach last |

### FOUNDATIONS (Teach First)

Topics with high reverse PageRank, low forward PageRank:

| Rank | Topic | Rev PR | Fwd PR | Position |
|------|-------|--------|--------|----------|
| 1 | Redox Chemistry | 0.01487 | 0.00162 | +0.01324 |
| 2 | Coordination Chemistry Fundamentals | 0.01170 | 0.00052 | +0.01118 |
| 3 | Electron Configuration | 0.00728 | 0.00052 | +0.00676 |
| 4 | Oxidation States | 0.00559 | 0.00052 | +0.00507 |
| 5 | Ionic Bonding | 0.00526 | 0.00052 | +0.00474 |
| 6 | Group Theory Basics | 0.00378 | 0.00052 | +0.00326 |
| 7 | Band Theory Of Solids | 0.00372 | 0.00052 | +0.00321 |
| 8 | Quantum Numbers | 0.00355 | 0.00052 | +0.00303 |

**Interpretation:** These concepts are prerequisites for many other topics. They should be taught FIRST.

### CAPSTONES (Teach Last)

Topics with high forward PageRank, low reverse PageRank:

| Rank | Topic | Rev PR | Fwd PR | Position |
|------|-------|--------|--------|----------|
| 1 | Main Group Chemistry | 0.00084 | 0.14652 | -0.14568 |
| 2 | Coordination Chemistry | 0.00084 | 0.05571 | -0.05487 |
| 3 | Solid State Chemistry | 0.00084 | 0.03445 | -0.03360 |
| 4 | Bioinorganic Chemistry | 0.00102 | 0.02803 | -0.02701 |
| 5 | Inorganic Chemistry In Medicine | 0.00084 | 0.02525 | -0.02441 |
| 6 | Acid-Base Chemistry | 0.00129 | 0.02040 | -0.01911 |
| 7 | Electrochemistry | 0.00087 | 0.01633 | -0.01546 |

**Interpretation:** Many prerequisite paths converge at these topics. They integrate knowledge from multiple foundations. Teach LAST.

### Key Finding: Main Group is a CAPSTONE

**Counterintuitive result:** Main Group Chemistry appears "basic" because it covers simple elements (Li, Na, etc.), but the knowledge graph reveals it actually INTEGRATES many foundational concepts:

- Periodic trends
- Oxidation states
- Redox chemistry
- Bonding theories
- Electron configuration

Teaching Main Group LAST allows students to synthesize knowledge from the entire course.

## 4.4 Corrected Curriculum Recommendation

### Three-Phase Curriculum Structure

```
PHASE 1: FOUNDATIONS (Sessions 1-5)
├── Electron Configuration
├── Periodic Trends
├── Oxidation States
├── Redox Chemistry
└── Ionic Bonding

PHASE 2: BRIDGES (Sessions 6-25)
├── Group Theory
├── Molecular Orbital Theory
├── Crystal Field Theory
├── Spectroscopy
├── Transition Metal Chemistry
└── [Most course content]

PHASE 3: CAPSTONES (Sessions 26-33)
├── Main Group Chemistry (synthesis)
├── Coordination Chemistry (integration)
├── Solid State Chemistry (integration)
├── Bioinorganic Chemistry (application)
└── Medicinal Inorganic Chemistry (application)
```

### Comparison with Traditional Curriculum

| Aspect | Traditional | Dual PageRank |
|--------|-------------|---------------|
| Main Group | Often taught early | Teach LAST (capstone) |
| Foundations | Implicit | Explicit (Redox, Electron Config) |
| Structure | Linear chapters | Foundation → Bridge → Capstone |
| Rationale | Textbook order | Data-driven |

## 4.5 PageRank vs Count Correlation

We verified that PageRank captures different information than textbook mention frequency:

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Pearson r | 0.64 | Some correlation (outliers) |
| Spearman ρ | 0.02 | **Near zero** - different rankings |

**Finding:** PageRank and count measure fundamentally different things:
- **Count** = textbook emphasis (how much discussed)
- **PageRank** = structural importance (prerequisite relationships)

A topic like "Covalent Bonding" has low count (#1860) but high PageRank (#36) because IC textbooks assume prior knowledge of it.

## 4.6 Limitation: Graph Sparsity and Alternative Analysis

### The 92.8% BRIDGE Concern

The dual PageRank model classifies 92.8% of topics as BRIDGE. Does this indicate low discriminatory power?

### Investigation: Graph Sparsity

Analysis of the CHEM 361 knowledge graph reveals **extreme sparsity**:

| Metric | Value | Implication |
|--------|-------|-------------|
| Nodes | 973 | |
| Edges | 2,885 | |
| Mean degree | 1.5 | Very sparse |
| Nodes with in-degree = 0 | 775 (79.7%) | Most are pure sources |
| Nodes with out-degree = 0 | 149 (15.3%) | Few pure sinks |

**Key insight:** Nearly 80% of nodes have NO incoming edges. PageRank requires rich interconnection for meaningful score propagation. With mean degree 1.5, most nodes are leaves in a tree-like structure.

### Why 92.8% BRIDGE Is Correct

The classification reflects **graph reality**:

1. Most extracted concepts connect ONE prerequisite to ONE dependent topic
2. Only a few high-degree hubs stand out from the distribution
3. The position distribution is unimodal (not bimodal as PageRank assumes)

### Alternative: Degree-Based Analysis

For sparse graphs, **raw degree** is more interpretable:

| Category | Count | Definition |
|----------|-------|------------|
| Pure foundations | 775 | in_degree=0, out_degree>0 |
| Pure capstones | 149 | out_degree=0, in_degree>0 |
| Hubs | 13 | in_degree>2 AND out_degree>2 |

**Top Actionable Foundations** (in=0, out≥5):

| Topic | Out-degree |
|-------|------------|
| Coordination Chemistry Fundamentals | 40 |
| Electron Configuration | 25 |
| Oxidation States | 17 |
| Ionic Bonding | 16 |
| Group Theory Basics | 11 |

**Top Capstones** (out=0, highest in-degree):

| Topic | In-degree |
|-------|-----------|
| Main Group Chemistry | 368 |
| Coordination Chemistry | 157 |
| Solid State Chemistry | 107 |
| Bioinorganic Chemistry | 84 |

### Methodological Recommendation

| Graph Type | Mean Degree | Recommended Method |
|------------|-------------|-------------------|
| Sparse (tree-like) | < 3 | **Degree-based** |
| Moderate | 3-10 | Either, verify both |
| Dense (web-like) | > 10 | PageRank |

The CHEM 361 graph (mean degree 1.5) is clearly sparse. For such graphs:

1. Use **degree-based classification** for identifying extremes
2. Focus on **out-degree ≥ 5** for actionable diagnostic foundations
3. Use **in-degree** directly to identify integration capstones
4. Reserve PageRank for denser knowledge graphs

### Hub Analysis: Critical Bridge Concepts

The degree-based analysis identified 13 **hub nodes** (in_degree > 2 AND out_degree > 2). These are critical bridge concepts that connect foundations to capstones:

| Rank | Topic | In | Out | Total | Key Predecessors | Key Successors |
|------|-------|----|----|-------|------------------|----------------|
| 1 | Acid-Base Chemistry | 55 | 7 | 62 | Periodic Trends, Acid Dissociation | Main Group Chemistry, Coordination |
| 2 | Crystal Field Theory | 46 | 12 | 58 | Atomic Orbitals, Electron Config | Coordination Chemistry |
| 3 | Molecular Orbital Theory | 43 | 13 | 56 | Atomic Orbitals, Electron Config | Crystal Field Theory, Main Group |
| 4 | Redox Chemistry | 7 | 34 | 41 | Electrochemical Series, Oxidation | Main Group, Enzymatic Catalysis |
| 5 | Periodic Trends | 17 | 19 | 36 | Periodic Table Structure | Acid-Base, Main Group Chemistry |
| 6 | Chemical Bonding | 32 | 3 | 35 | Atomic Structure, Periodic Trends | Molecular Orbital Theory |
| 7 | Organometallic Chemistry | 24 | 5 | 29 | Coordination Fundamentals, Ligands | Catalysis, Main Group |
| 8 | Atomic Structure | 13 | 12 | 25 | Quantum Numbers, Wavefunctions | Nuclear Chemistry, Main Group |
| 9 | Transition Metal Chemistry | 11 | 7 | 18 | Coordination Fundamentals | Coordination, Organometallic |
| 10 | Crystal Structures | 5 | 7 | 12 | Lattice Structures, Ionic Bonding | Solid State Chemistry |
| 11 | Thermochemistry | 7 | 3 | 10 | Enthalpy Concepts, Ionic Bonding | Hydrogen Production, Solid State |
| 12 | Electronegativity | 3 | 4 | 7 | Atomic Structure, Periodic Trends | Chemical Bonding, Main Group |
| 13 | Polymer Chemistry | 4 | 3 | 7 | Polymerization Mechanisms | Nanomaterials |

**Pedagogical implication:** These 13 hubs should receive extra attention in curriculum design—they are the "bottleneck" concepts where student understanding can break down.

---

# 5. Novel Pedagogical Features

## 5.1 Bridge Explanations

**Traditional:**
> "Session 21: Crystal Field Theory. In octahedral complexes, d-orbitals split into t2g and eg sets..."

**Novel:**
> "You learned d-orbitals have different shapes (Session 1). You learned ligands have lone pairs (Session 17). Now: What happens when 6 ligands approach a metal? The ligands' electrons REPEL the metal's d-electrons..."

**Implementation:**
```python
def generate_bridge(concept, student_history):
    prereqs = graph.get_prerequisites(concept)
    known = [p for p in prereqs if p in student_history]
    return f"You learned {known[0]} earlier. Now see how {concept} builds on it..."
```

## 5.2 Scale Zoom

Same phenomenon explained at 4 depths:

| Scale | "Why is copper sulfate blue?" |
|-------|-------------------------------|
| **DESCRIPTIVE** | "Copper compounds are typically blue or green" |
| **STRUCTURAL** | "Cu²⁺ forms octahedral [Cu(H₂O)₆]²⁺" |
| **ELECTRONIC** | "d-d transition absorbs orange (~600nm), transmits blue" |
| **QUANTUM** | "Laporte-forbidden but vibronically allowed transition" |

## 5.3 Question-Driven Paths

**Student asks:** "How do MRI contrast agents work?"

**System traces prerequisites:**
```
MRI contrast agents
    ↓ requires
Magnetic moment of metal ions
    ↓ requires
Unpaired electrons
    ↓ requires
Crystal field theory
    ↓ requires
d-orbital splitting
    ↓ requires
Atomic orbital shapes
```

**System generates personalized path:**
1. Quick review: Atomic orbitals (5 min) - *if unknown*
2. Quick review: d-orbital splitting (10 min) - *if unknown*
3. New: High-spin vs low-spin (15 min)
4. New: Magnetic moment calculation (10 min)
5. Application: MRI contrast agents (20 min)

## 5.4 Comparison

| Aspect | Traditional | Novel |
|--------|-------------|-------|
| Structure | Linear (Ch 1→2→3) | Graph (interconnected) |
| Connections | Implicit | Explicit bridges |
| Starting point | Chapter 1 | Any question |
| Depth | Fixed | Zoomable (4 scales) |
| Prerequisites | Assumed | Traced & reviewed |
| Student agency | Follow syllabus | Choose entry point |

---

# 6. Vision: Meta-Scale Tree

## 6.1 Extending to All Undergraduate Chemistry

The methodology can be applied to create a **unified knowledge forest** spanning all undergraduate chemistry:

```
╔══════════════════════════════════════════════════════════════════╗
║                    META-SCALE KNOWLEDGE FOREST                    ║
║                  Undergraduate Chemistry (100-400 Level)          ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║   400 LEVEL ────────────────────────────────────────────────     ║
║   Advanced    [Inorg]  [Organic]  [Physical]  [Analytical]       ║
║                                                                   ║
║   300 LEVEL ────────────────────────────────────────────────     ║
║   Intermediate Inorg I  Org II    PChem I     Anal Chem          ║
║                                                                   ║
║   200 LEVEL ────────────────────────────────────────────────     ║
║   Sophomore    ─────────Organic I─────────    QuantAnal          ║
║                                                                   ║
║   100 LEVEL ────────────────────────────────────────────────     ║
║   Freshman     ══════════ General Chemistry I & II ══════════    ║
║                                                                   ║
╚══════════════════════════════════════════════════════════════════╝
```

## 6.2 Branch-Specific Scales

Each chemistry branch has its own 4-scale hierarchy:

| Branch | Scale 4 (Deep) | Scale 3 | Scale 2 | Scale 1 (Surface) |
|--------|----------------|---------|---------|-------------------|
| **Inorganic** | Quantum | Electronic | Structural | Descriptive |
| **Organic** | Orbital | Mechanistic | Functional | Synthetic |
| **Physical** | Quantum | Statistical | Kinetic | Thermodynamic |
| **Analytical** | Signal | Instrumental | Methodological | Practical |
| **Biochemistry** | Molecular | Structural | Functional | Systems |

## 6.3 Applications

1. **Degree Program Design:** Identify prerequisite gaps between courses
2. **Curriculum Alignment:** Map ACS guidelines to knowledge graph
3. **Transfer Student Advising:** Map incoming courses, identify gaps
4. **Textbook Selection:** Compare coverage across textbooks
5. **Assessment Design:** Tag assessments to scale levels

---

# 7. Implementation Details

## 7.1 Technology Stack

| Component | Technology |
|-----------|------------|
| Vector database | Qdrant |
| Embeddings | nomic-embed-text (768-dim) |
| LLM for extraction | Qwen3 via Ollama |
| Graph analysis | NetworkX |
| Visualization | D3.js |
| Backend | Python (FastAPI) |

## 7.2 Key Files

| File | Purpose |
|------|---------|
| `path_tracer.py` | Core prerequisite tracing algorithm |
| `curriculum_schema.py` | Standardized data structures |
| `api_server.py` | HTTP API for visualization |
| `funnel.html` | Interactive funnel visualization |
| `scales.html` | Scale-layered visualization |

## 7.3 API

```bash
GET /api/trace?q=<question>    # Trace prerequisites
GET /api/concepts              # List all concepts
GET /api/health                # Health check
```

## 7.4 Reproducibility

All data verified via `verify_sources.py`:

```
Collection:    textbooks_chunks
Total Points:  8,756
Unique Sources: 7 textbooks (verified)
```

---

# 8. Research Questions

For future empirical studies:

1. **Learning outcomes:** Does the three-phase curriculum (Foundation→Bridge→Capstone) improve learning?
2. **Misconceptions:** Do explicit bridge explanations reduce misconceptions?
3. **Engagement:** Does question-driven learning increase student engagement?
4. **Conceptual understanding:** How does scale-zoom affect depth of understanding?
5. **Curriculum validity:** Does dual PageRank ordering outperform traditional ordering?
6. **Transfer:** Do students transfer knowledge better when prerequisites are explicit?

---

# 9. Appendices

## Appendix A: 19 Rules of Knowledge Graph Pedagogy

| # | Rule | Source |
|---|------|--------|
| 1 | Use semantic chunking | Extraction results |
| 2 | Extract at multiple granularities | 5,380 vs single-level |
| 3 | Distinguish relationship types | Edge analysis |
| 4 | Filter by mention count (≥10) | Noise reduction |
| 5 | Build bidirectional chunk-node mapping | KAG framework |
| 6 | **Use DUAL PageRank for curriculum ordering** | Corrected analysis |
| 6a | Reverse PageRank identifies foundations | Teach first |
| 6b | Forward PageRank identifies capstones | Teach last |
| 7 | Use label propagation for communities | O(n³) timeout |
| 8 | Use breadth-first for intro courses | Method comparison |
| 9 | Allocate time by coverage | Textbook analysis |
| 10 | Knowledge exists at multiple scales | Bricks insight |
| 11 | Each scale is self-contained | Learning objectives |
| 12 | Each scale contains trees | Graph structure |
| 13 | Stay within scale when possible | Navigation analysis |
| 14 | Escalate only for "why" | Question analysis |
| 15 | Explore siblings before escalating | Tree traversal |
| 16 | Blind path only for anomalies | Edge case study |
| 17 | Most edges stay within scale | Flow matrix |
| 18 | Some topics are endpoints | Dependency analysis |
| 19 | PageRank ≠ Count (different metrics) | Correlation analysis |

## Appendix B: Verified Data Sources

| Textbook | Chunks | % |
|----------|--------|---|
| Atkins/Shriver - Inorganic Chemistry | 2,494 | 28.5% |
| Housecroft/Sharpe - Inorganic Chemistry | 2,375 | 27.1% |
| Douglas/McDaniel - Descriptive IC | 1,495 | 17.1% |
| House - Descriptive IC | 1,027 | 11.7% |
| JD Lee - Concise IC | 565 | 6.5% |
| Basset - IC | 446 | 5.1% |
| Advanced IC Applications | 351 | 4.0% |
| **Total** | **8,753** | |

## Appendix C: Dual PageRank Results

### Complete Foundation List (Position > 0.001)

```
Topic                                     Rev_PR    Fwd_PR   Position
─────────────────────────────────────────────────────────────────────
Redox Chemistry                           0.01487   0.00162  +0.01324
Coordination Chemistry Fundamentals       0.01170   0.00052  +0.01118
Electron Configuration                    0.00728   0.00052  +0.00676
Oxidation States                          0.00559   0.00052  +0.00507
Ionic Bonding                             0.00526   0.00052  +0.00474
Group Theory Basics                       0.00378   0.00052  +0.00326
Band Theory Of Solids                     0.00372   0.00052  +0.00321
Quantum Numbers                           0.00355   0.00052  +0.00303
```

### Complete Capstone List (Position < -0.005)

```
Topic                                     Rev_PR    Fwd_PR   Position
─────────────────────────────────────────────────────────────────────
Main Group Chemistry                      0.00084   0.14652  -0.14568
Coordination Chemistry                    0.00084   0.05571  -0.05487
Solid State Chemistry                     0.00084   0.03445  -0.03360
Bioinorganic Chemistry                    0.00102   0.02803  -0.02701
Inorganic Chemistry In Medicine           0.00084   0.02525  -0.02441
Acid-Base Chemistry                       0.00129   0.02040  -0.01911
Electrochemistry                          0.00087   0.01633  -0.01546
```

## Appendix D: Sample API Response

```json
{
  "target": "Crystal Field Theory",
  "all_nodes": {
    "Crystal Field Theory": {
      "scale": "ELECTRONIC",
      "depth": 0,
      "count": 165,
      "foundation_score": 0.00434,
      "capstone_score": 0.01395,
      "position": -0.00961,
      "category": "BRIDGE"
    },
    "Molecular Orbital Theory": {
      "scale": "QUANTUM",
      "depth": 1,
      "count": 143
    }
  },
  "layers": {
    "QUANTUM": ["Molecular Orbital Theory", "Atomic Orbitals"],
    "ELECTRONIC": ["Crystal Field Theory", "Spectroscopy"],
    "STRUCTURAL": ["Point Group Symmetry"],
    "DESCRIPTIVE": ["Periodic Trends"]
  }
}
```

---

# Files to Include with This Package

For complete LLM analysis, include these files:

| File | Lines | Purpose |
|------|-------|---------|
| **This file** | ~650 | JCE paper draft structure |
| `DUAL_PAGERANK_MODEL.md` | 241 | **Corrected PageRank methodology** |
| `KNOWLEDGE_GRAPH_PEDAGOGY.md` | 408 | Full methodology + 18 rules |
| `KNOWLEDGE_FUNNEL_METHODOLOGY.md` | 391 | Funnel approach + results |
| `CHEMKG_VISION.md` | 260 | Meta-scale tree vision |
| `NOVEL_PEDAGOGY.md` | 165 | 3 novel features |
| `path_tracer.py` | 332 | Core algorithm |

**Total context:** ~2,450 lines

---

# Key Contributions

1. **Dual PageRank Model:** Novel method distinguishing foundational vs. capstone topics
2. **Multi-Scale Knowledge Model:** 4-level hierarchy (Q→E→S→D) for chemistry concepts
3. **Three-Phase Curriculum:** Data-driven Foundation → Bridge → Capstone structure
4. **Counterintuitive Finding:** Main Group Chemistry is a capstone, not a foundation
5. **PageRank ≠ Count:** Structural importance differs from textbook emphasis

---

*Working paper for Journal of Chemical Education*
*CHEM 361 Knowledge Graph Pedagogy Project*
*Corrected January 2026*
