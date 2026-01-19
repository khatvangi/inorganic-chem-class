# Curriculum Generator: Data-Driven Course Sequencing

**Purpose:** Generate optimal topic ordering from knowledge graph using multiple algorithms
**File:** `experiments/curriculum_generator.py`
**Last Updated:** 2026-01-18

---

## Overview

The Curriculum Generator uses the ChemKG knowledge graph to produce data-driven course sequences. Rather than relying solely on instructor intuition or textbook chapter order, it analyzes prerequisite relationships, topic centrality, and textbook coverage to recommend pedagogically sound orderings.

```
┌─────────────────────────────────────────────────────────────────┐
│                  Curriculum Generator Pipeline                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────┐                                           │
│   │  Knowledge Graph │                                          │
│   │  (5,380 nodes)   │                                          │
│   └────────┬────────┘                                           │
│            │                                                     │
│            ▼                                                     │
│   ┌─────────────────┐                                           │
│   │  Extract Topics  │  1,017 topic nodes                       │
│   │  + PageRank      │  + centrality scores                     │
│   │  + Prerequisites │  + dependency edges                      │
│   └────────┬────────┘                                           │
│            │                                                     │
│            ▼                                                     │
│   ┌─────────────────────────────────────────────┐               │
│   │           8 Ordering Algorithms              │               │
│   ├─────────────────────────────────────────────┤               │
│   │ Topological │ PageRank  │ Hybrid   │Coverage│               │
│   │ Depth-First │ Breadth-1st│Community│Difficulty│              │
│   └────────┬────────────────────────────────────┘               │
│            │                                                     │
│            ▼                                                     │
│   ┌─────────────────┐                                           │
│   │ Ranked Curriculum│  Ordered list of topics                  │
│   │ with Metadata    │  + mentions, PageRank, prereqs           │
│   └─────────────────┘                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## The 8 Ordering Methods

### 1. Topological Sort

**Algorithm:** Kahn's algorithm (BFS-based)

**Principle:** Respects prerequisite constraints absolutely. A topic only appears after all its prerequisites.

**Best for:** Strict prerequisite ordering where missing foundations cause failure.

```python
def topological_sort(self):
    # Kahn's algorithm with tie-breaking by mention count
    # Topics with no prerequisites come first
    # Among equals, pick most-mentioned
```

**Characteristics:**
- Guarantees no forward references
- May produce fewer topics (only those with explicit edges)
- Tie-breaking by mention count prioritizes well-covered topics

### 2. PageRank Order

**Algorithm:** Power iteration (damping=0.85)

**Principle:** Topics that many other topics depend on have higher centrality. Teach the most fundamental concepts first.

**Best for:** Foundations-first approach; identifying core concepts.

```python
def pagerank_order(self):
    # Sort by PageRank score descending
    # Ignores prerequisite constraints
    # Pure centrality ranking
```

**Top 10 by PageRank:**
| Rank | Topic | PageRank |
|------|-------|----------|
| 1 | Main Group Chemistry | 0.0204 |
| 2 | Periodic Trends | 0.0120 |
| 3 | Redox Chemistry | 0.0079 |
| 4 | Coordination Chemistry | 0.0049 |
| 5 | Solid State Chemistry | 0.0039 |
| 6 | Molecular Orbital Theory | 0.0030 |
| 7 | Atomic Structure | 0.0030 |
| 8 | Chemical Bonding | 0.0029 |
| 9 | Acid-Base Chemistry | 0.0025 |
| 10 | Crystal Field Theory | 0.0017 |

### 3. Hybrid Order

**Algorithm:** Greedy selection with PageRank scoring

**Principle:** At each step, pick the highest-PageRank topic whose prerequisites are satisfied.

**Best for:** Balancing fundamentality with prerequisite constraints.

```python
def hybrid_order(self):
    # Greedy: pick max PageRank from ready topics
    # Ready = all prereqs already scheduled
    # Breaks cycles by picking highest PR from remaining
```

**Characteristics:**
- Combines benefits of topological + PageRank
- Handles cycles gracefully
- Preferred for real curriculum design

### 4. Coverage Order

**Algorithm:** Sort by mention count

**Principle:** Topics emphasized by more textbooks (higher mention count) come first.

**Best for:** Matching textbook emphasis; allocating time proportionally.

```python
def coverage_order(self):
    # Sort by self.topics[t].get("count", 0) descending
```

**Coverage Distribution:**
| Topic | Mentions | % of Total |
|-------|----------|------------|
| Main Group Chemistry | 1,570 | 20.3% |
| Coordination Chemistry | 1,271 | 16.5% |
| Solid State Chemistry | 427 | 5.5% |
| Electrochemistry | 255 | 3.3% |
| Acid-Base Chemistry | 194 | 2.5% |

### 5. Depth-First Order

**Algorithm:** DFS from high-PageRank seeds

**Principle:** Master one branch deeply before moving to the next.

**Best for:** "Deep dive" pedagogy; specialization tracks.

```python
def depth_first_order(self, start_topics=None):
    # DFS from top-5 PageRank topics
    # Visit dependents sorted by PageRank
    # Go deep before going broad
```

**Characteristics:**
- Creates focused learning paths
- May delay foundational cross-cutting topics
- Good for advanced/specialized courses

### 6. Breadth-First Order

**Algorithm:** BFS from high-PageRank seeds

**Principle:** Cover all fundamentals first, then advance layer by layer.

**Best for:** Building broad foundation before specialization.

```python
def breadth_first_order(self, start_topics=None):
    # BFS from top-5 PageRank topics
    # Cover all level-1 before level-2
    # Ensures broad exposure early
```

**Characteristics:**
- Ensures foundational coverage
- Natural progression from basic to advanced
- Recommended for introductory courses

### 7. Community-Based Order

**Algorithm:** Label propagation clustering + intra-community PageRank

**Principle:** Group related topics together; teach thematic units.

**Best for:** Modular curriculum; thematic coherence.

```python
def community_order(self):
    # Label propagation (O(E) complexity)
    # Sort communities by total PageRank
    # Within community, sort by PageRank
```

**Communities Detected:**
| Community | Topics | Total PageRank |
|-----------|--------|----------------|
| Periodic/Atomic | 45 | 0.0512 |
| Coordination | 38 | 0.0298 |
| Solid State | 22 | 0.0187 |
| Electrochemistry | 12 | 0.0089 |

### 8. Difficulty-Based Order

**Algorithm:** Count transitive prerequisites

**Principle:** Simpler topics (fewer prerequisites) come first.

**Best for:** Scaffolding; ensuring students aren't overwhelmed.

```python
def difficulty_order(self):
    # BFS to count all transitive prerequisites
    # Sort by difficulty ascending
    # Tie-break by mention count
```

**Characteristics:**
- Explicit scaffolding
- May not match conceptual difficulty
- Useful for identifying "gateway" topics

---

## Usage

### Command Line

```bash
cd /storage/inorganic-chem-class
source /storage/RAG/.venv/bin/activate

# compare all methods
python experiments/curriculum_generator.py --method all --top 25

# single method with export
python experiments/curriculum_generator.py --method hybrid --export curriculum.json

# adjust significance threshold
python experiments/curriculum_generator.py --min-count 20 --top 30
```

### Python API

```python
from curriculum_generator import CurriculumGenerator

gen = CurriculumGenerator()

# get ordered list
order = gen.hybrid_order(min_count=10)

# generate all and compare
curricula = gen.generate_all(min_count=10, top_n=30)

# export with metadata
curriculum = gen.export_curriculum(
    method="breadth_first",
    min_count=10,
    output_file="my_curriculum.json"
)

# print comparison table
gen.print_comparison(min_count=10, top_n=25)
```

### CLI Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--method` | `all` | Ordering method or "all" for comparison |
| `--min-count` | `10` | Minimum mentions to include topic |
| `--top` | `30` | Number of topics to display |
| `--export` | None | Export to JSON file |

---

## Output Format

### JSON Export

```json
{
  "method": "hybrid",
  "min_count": 10,
  "total_topics": 67,
  "topics": [
    {
      "rank": 1,
      "topic": "Main Group Chemistry",
      "mentions": 1570,
      "pagerank": 0.0204,
      "prerequisites": ["Periodic Trends", "Atomic Structure"],
      "leads_to": ["Coordination Chemistry", "Solid State Chemistry"]
    }
  ]
}
```

### Comparison Output

```
================================================================================
CURRICULUM COMPARISON (8 Methods)
================================================================================

--- TOPOLOGICAL (67 topics) ---
   1. Descriptive Inorganic Chemistry    (  65 mentions, PR:0.0001)
   2. Atomic Structure                   (  38 mentions, PR:0.0030)
   ...

--- PAGERANK (67 topics) ---
   1. Main Group Chemistry               (1570 mentions, PR:0.0204)
   2. Periodic Trends                    (  74 mentions, PR:0.0120)
   ...
```

---

## Key Finding: Curriculum Reorder Recommendation

Analysis of the CHEM 361 knowledge graph revealed a significant insight:

### Existing vs Data-Driven Order

| Aspect | Existing | Data-Driven |
|--------|----------|-------------|
| **Order** | Coordination → Main Group → Solid State | Main Group → Coordination → Solid State |
| **Unit 1** | Coordination (9 sessions) | Main Group (9 sessions) |
| **Unit 2** | Main Group (7 sessions) | Coordination (10 sessions) |
| **Unit 3** | Solid State (7 sessions) | Solid State (4 sessions) |

### Why Main Group First?

1. **Highest PageRank (0.0432):** Most other topics depend on main group concepts
2. **Prerequisite Structure:** Periodic trends → Crystal Field Theory
3. **Textbook Coverage (40%):** Textbooks spend significant time on fundamentals
4. **Conceptual Flow:** Atomic properties → Bonding → Coordination complexes

### Visualization

```
EXISTING CURRICULUM:
  Week 1-5:  Coordination Chemistry (Crystal Field Theory, Ligands, ...)
  Week 6-10: Main Group Chemistry (Periodic Trends, Elements, ...)
  Week 11-15: Solid State Chemistry

DATA-DRIVEN RECOMMENDATION:
  Week 1-5:  Main Group Chemistry (Foundations, Periodic Trends, ...)
  Week 6-10: Coordination Chemistry (Crystal Field Theory, ...)
  Week 11-15: Solid State Chemistry (reduced, proportional to coverage)
```

---

## Method Selection Guide

| If you want... | Use this method |
|----------------|-----------------|
| Strict prerequisites | `topological` |
| Fundamentals first | `pagerank` or `breadth_first` |
| Balanced approach | `hybrid` (recommended) |
| Match textbook time | `coverage` |
| Deep specialization | `depth_first` |
| Thematic units | `community` |
| Scaffolded difficulty | `difficulty` |

---

## Integration with ChemKG-RAG

The curriculum generator uses the same enhanced graph as ChemKG-RAG:

```python
# both tools share the same data
GRAPH_FILE = "experiments/results/chemkg_enhanced.json"

# curriculum generator uses:
# - nodes with type="topic"
# - edges with relation="prerequisite_for" or "leads_to"
# - pagerank scores computed by ChemKG-RAG
```

---

## Data Files

| File | Description |
|------|-------------|
| `experiments/results/chemkg_enhanced.json` | Source graph with PageRank |
| `experiments/results/recommended_curriculum.json` | Breadth-first curriculum |
| `experiments/results/curriculum_comparison.json` | Existing vs data-driven |

---

## Limitations

1. **Topic Granularity:** "Main Group Chemistry" is broad; may need subtopics
2. **Sparse Prerequisites:** Not all topic pairs have explicit edges
3. **No Time Estimation:** Methods order topics but don't estimate duration
4. **Single Graph:** Based on 7 textbooks; may not generalize

---

## References

- Kahn's Algorithm: Kahn, A.B. (1962). "Topological sorting of large networks"
- PageRank: Page, L. et al. (1999). "The PageRank Citation Ranking"
- Label Propagation: Raghavan, U.N. et al. (2007). "Near linear time algorithm to detect community structures"

---

*Part of the Knowledge Graph Pedagogy Project*
*McNeese State University, CHEM 361*
