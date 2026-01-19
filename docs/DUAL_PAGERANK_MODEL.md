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

## References

- NetworkX PageRank: `nx.pagerank(G, alpha=0.85)`
- Original PageRank: Brin & Page (1998)
- Reverse PageRank for finding sources: Various network analysis literature

---

*Model developed: January 2026*
*Corrects original single-PageRank analysis*
