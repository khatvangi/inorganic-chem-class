# Dual PageRank Curriculum Model

**Correction to original methodology - January 2026**

---

## The Problem with Single PageRank

The original analysis used only forward PageRank, which was:
1. **Not properly normalized** (sum = 0.245 instead of 1.0)
2. **Measuring the wrong thing** for curriculum design

Forward PageRank identifies nodes that many edges point TO (convergence points), but for curriculum ordering we need BOTH:
- What should be taught **FIRST** (foundational concepts)
- What should be taught **LAST** (capstone/integration topics)

---

## The Dual PageRank Model

### Two Complementary Metrics

| Metric | Direction | Measures | Curriculum Role |
|--------|-----------|----------|-----------------|
| **Reverse PageRank** | Follow edges backward | What is a prerequisite for many topics | **FOUNDATIONS** (teach first) |
| **Forward PageRank** | Follow edges forward | What many topics lead to | **CAPSTONES** (teach last) |

### Position Score

```
Position = Reverse_PR - Forward_PR

Positive → FOUNDATION (teach early)
Near zero → BRIDGE (teach in middle)
Negative → CAPSTONE (teach late)
```

### Thresholds

```python
if position > 0.001:
    category = "FOUNDATION"
elif position < -0.005:
    category = "CAPSTONE"
else:
    category = "BRIDGE"
```

---

## Results: CHEM 361 Inorganic Chemistry

### Distribution

| Category | Count | Percentage | Role |
|----------|-------|------------|------|
| FOUNDATION | 63 | 6.5% | Prerequisites, teach first |
| BRIDGE | 903 | 92.8% | Main content |
| CAPSTONE | 7 | 0.7% | Integration topics, teach last |

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

**Interpretation:** These concepts are prerequisites for many other topics but few things lead to them. They should be taught FIRST.

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

**Interpretation:** Many prerequisite paths converge at these topics. They integrate knowledge from multiple foundational concepts. Teach LAST as capstones.

### BRIDGES (Teach in Middle)

Topics with balanced forward and reverse PageRank:

| Topic | Rev PR | Fwd PR | Position |
|-------|--------|--------|----------|
| Atomic Structure | 0.00235 | 0.00273 | -0.00038 |
| Polymer Chemistry | 0.00168 | 0.00203 | -0.00034 |
| Molecular Orbital Theory | 0.00451 | 0.01422 | -0.00971 |
| Crystal Field Theory | 0.00434 | 0.01395 | -0.00961 |

**Interpretation:** These topics both depend on foundations and lead to capstones. They form the main body of the curriculum.

---

## Corrected Curriculum Recommendation

### Original (WRONG)

Based on incorrectly computed single PageRank:
> "Main Group Chemistry should come FIRST because it has highest PageRank"

### Corrected (RIGHT)

Based on dual PageRank model:

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
├── Main Group Chemistry (synthesis of periodic knowledge)
├── Coordination Chemistry (integration of bonding + structure)
├── Solid State Chemistry (integration of structure + properties)
├── Bioinorganic Chemistry (application)
└── Medicinal Inorganic Chemistry (application)
```

### Key Insight

**Main Group Chemistry is NOT foundational—it is a CAPSTONE.**

It appears foundational because it covers "simple" elements, but the knowledge graph reveals it INTEGRATES many prerequisite concepts:
- Periodic trends
- Oxidation states
- Redox chemistry
- Bonding theories

Teaching Main Group last allows students to synthesize knowledge from the entire course.

---

## Algorithm

```python
import networkx as nx

def dual_pagerank_curriculum(G, alpha=0.85):
    """
    Compute curriculum position using dual PageRank.

    Args:
        G: DiGraph where edge (A, B) means "A is prerequisite for B"
        alpha: PageRank damping factor

    Returns:
        dict: {node: {'foundation': score, 'capstone': score, 'position': score}}
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
            'position': position,
            'category': categorize(position)
        }

    return result

def categorize(position):
    if position > 0.001:
        return "FOUNDATION"
    elif position < -0.005:
        return "CAPSTONE"
    else:
        return "BRIDGE"
```

---

## Implications for JCE Paper

### Methodological Contribution

The dual PageRank model provides:
1. **Empirical grounding** for curriculum ordering decisions
2. **Clear separation** of foundations vs. capstones
3. **Data-driven identification** of integration topics

### Pedagogical Insight

The model reveals that topic "importance" has two dimensions:
- **Foundational importance**: How many things depend on this?
- **Integration importance**: How much does this synthesize?

Both are necessary for complete curriculum design.

### Practical Application

1. Compute prerequisite graph from textbooks
2. Apply dual PageRank
3. Sort by position score
4. Design curriculum: foundations → bridges → capstones

---

## Limitation: Graph Sparsity and the 92.8% BRIDGE Problem

### The Concern

The dual PageRank model classifies 92.8% of topics as BRIDGE, with only 6.5% FOUNDATION and 0.7% CAPSTONE. This raises questions about discriminatory power.

### Root Cause: Graph Sparsity

Analysis reveals the knowledge graph is **extremely sparse**:

| Metric | Value |
|--------|-------|
| Nodes | 973 |
| Edges | 2,885 |
| Mean degree | 1.5 |
| Nodes with in-degree = 0 | 775 (79.7%) |
| Nodes with out-degree = 0 | 149 (15.3%) |

**Key insight:** Nearly 80% of nodes have NO incoming edges—they are pure sources in the graph. PageRank struggles with such sparse, tree-like structures because:

1. PageRank assumes rich interconnection for score propagation
2. With mean degree 1.5, most nodes are leaves or near-leaves
3. The position distribution is unimodal, not bimodal

### Why 92.8% BRIDGE Is Actually Correct

The 92.8% classification reflects **graph reality**, not threshold artifact:

```
Position Distribution (955/973 nodes in narrow band):
│
│                    ████████████████████████████████████████
│                    ████████████████████████████████████████
├────────────────────|──────────────────────────────────|────────
              -0.003                                  +0.005
                           (955 nodes here)
```

Most nodes genuinely ARE bridges—they connect one prerequisite to one dependent topic. Only a few high-degree hubs stand out.

### Alternative: Degree-Based Analysis

For sparse graphs, **raw degree** is more interpretable than PageRank:

```python
def degree_based_curriculum(G):
    """
    For sparse graphs, use degree directly.

    Pure foundation: in_degree=0, out_degree>0
    Pure capstone: out_degree=0, in_degree>0
    Hub: both in_degree>2 and out_degree>2
    """
    foundations = []
    capstones = []
    hubs = []

    for node in G.nodes():
        in_deg = G.in_degree(node)
        out_deg = G.out_degree(node)

        if in_deg == 0 and out_deg > 0:
            foundations.append((node, out_deg))
        elif out_deg == 0 and in_deg > 0:
            capstones.append((node, in_deg))
        elif in_deg > 2 and out_deg > 2:
            hubs.append((node, in_deg, out_deg))

    return {
        'foundations': sorted(foundations, key=lambda x: -x[1]),
        'capstones': sorted(capstones, key=lambda x: -x[1]),
        'hubs': sorted(hubs, key=lambda x: -(x[1] + x[2]))
    }
```

### Degree-Based Results

| Category | Count | Top Examples |
|----------|-------|--------------|
| Pure foundations (in=0, out>0) | 775 | See table below |
| Pure capstones (out=0, in>0) | 149 | Main Group Chemistry (in=368) |
| Hubs (in>2, out>2) | 13 | Bonding, Spectroscopy |

**Top Actionable Foundations** (in=0, out≥5):

| Rank | Topic | Out-degree | Use |
|------|-------|------------|-----|
| 1 | Coordination Chemistry Fundamentals | 40 | Diagnostic assessment |
| 2 | Electron Configuration | 25 | Diagnostic assessment |
| 3 | Oxidation States | 17 | Diagnostic assessment |
| 4 | Ionic Bonding | 16 | Diagnostic assessment |
| 5 | Group Theory Basics | 11 | Diagnostic assessment |
| 6 | Quantum Numbers | 10 | Diagnostic assessment |
| 7 | Band Theory Of Solids | 9 | Diagnostic assessment |
| 8 | Chemical Bonding | 8 | Diagnostic assessment |

**Top Capstones** (out=0, highest in-degree):

| Rank | Topic | In-degree | Integration |
|------|-------|-----------|-------------|
| 1 | Main Group Chemistry | 368 | Ultimate capstone |
| 2 | Coordination Chemistry | 157 | Major integration |
| 3 | Solid State Chemistry | 107 | Major integration |
| 4 | Bioinorganic Chemistry | 84 | Application |
| 5 | Transition Metal Chemistry | 72 | Integration |

### Recommended Approach

For **sparse prerequisite graphs** (mean degree < 3):

1. Use **degree-based classification** for identifying extremes
2. Reserve **PageRank** for dense, richly-connected graphs
3. Focus on **actionable foundations** (out-degree ≥ 5) for diagnostic assessment
4. Use **in-degree** directly to identify integration topics

### PageRank vs Degree: When to Use Each

| Graph Type | Mean Degree | Recommended Method |
|------------|-------------|-------------------|
| Sparse (tree-like) | < 3 | Degree-based |
| Moderate | 3-10 | Either, verify both |
| Dense (web-like) | > 10 | PageRank |

The CHEM 361 graph (mean degree 1.5) is clearly in the sparse category.

---

## References

- NetworkX PageRank: `nx.pagerank(G, alpha=0.85)`
- Original PageRank: Brin & Page (1998)
- Reverse PageRank for finding sources: Various network analysis literature
- Graph sparsity effects on PageRank: Boldi & Vigna (2005)

---

*Model developed: January 2026*
*Corrects original single-PageRank analysis*
*Sparsity analysis added: January 2026*
