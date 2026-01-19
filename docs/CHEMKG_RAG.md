# ChemKG-RAG: Hybrid Knowledge Graph RAG for Inorganic Chemistry

**Purpose:** Q&A system combining 5 RAG frameworks for accurate chemistry answers
**File:** `experiments/chemkg_rag.py`
**Last Updated:** 2026-01-18

---

## Overview

ChemKG-RAG is a hybrid retrieval-augmented generation system that combines techniques from five state-of-the-art frameworks to answer complex inorganic chemistry questions using textbook knowledge.

```
┌─────────────────────────────────────────────────────────────────┐
│                      ChemKG-RAG Architecture                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│   │    KAG      │  │  HippoRAG   │  │    LAG      │             │
│   │   Mutual    │  │  PageRank   │  │   Question  │             │
│   │  Indexing   │  │  Prereqs    │  │ Decomposition│            │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│          │                │                │                     │
│          └────────────────┼────────────────┘                     │
│                           │                                      │
│                    ┌──────▼──────┐                               │
│                    │  LightRAG   │                               │
│                    │ Dual-Level  │                               │
│                    │  Retrieval  │                               │
│                    └──────┬──────┘                               │
│                           │                                      │
│                    ┌──────▼──────┐                               │
│                    │  GraphRAG   │                               │
│                    │ Cross-Book  │                               │
│                    │  Synthesis  │                               │
│                    └─────────────┘                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. KAG: Mutual Indexing

**Source:** [OpenSPG/KAG](https://github.com/OpenSPG/KAG)

**What it does:** Creates bidirectional links between knowledge graph nodes and source text chunks.

**Our implementation:**
```python
node_to_chunks: dict  # topic/concept → [chunk_ids]
chunk_to_nodes: dict  # chunk_id → [topic/concept ids]
```

**Statistics:**
- 5,339 nodes indexed
- 7,715 chunks linked
- Average 5.8 chunks per node

**Why it matters:** Enables retrieval of original textbook passages for any topic, grounding answers in source material.

### 2. HippoRAG: PageRank on Prerequisites

**Source:** [OSU-NLP-Group/HippoRAG](https://github.com/OSU-NLP-Group/HippoRAG)

**What it does:** Ranks topics by centrality in the prerequisite graph using PageRank algorithm.

**Our implementation:**
```python
def pagerank(damping=0.85, max_iter=100):
    # power iteration on prerequisite adjacency matrix
    # higher score = more fundamental concept
```

**Top 10 by PageRank (most fundamental):**
| Rank | Topic | PageRank |
|------|-------|----------|
| 1 | Main Group Chemistry | 0.0204 |
| 2 | Periodic Trends | 0.0120 |
| 3 | Redox Chemistry | 0.0079 |
| 4 | Coordination Chemistry | 0.0049 |
| 5 | Ionic Bonding | 0.0044 |
| 6 | Solid State Chemistry | 0.0039 |
| 7 | Periodic Table Structure | 0.0030 |
| 8 | Molecular Orbital Theory | 0.0030 |
| 9 | Atomic Structure | 0.0030 |
| 10 | Chemical Bonding | 0.0029 |

**Why it matters:** Identifies foundational concepts and ranks prerequisites by importance.

### 3. LAG: Sub-question Decomposition

**Source:** [LAG Paper](https://arxiv.org/abs/2411.14012)

**What it does:** Decomposes complex questions into atomic sub-questions with dependency ordering.

**Our implementation:**
```python
def decompose_question(question: str) -> list:
    # LLM extracts sub-questions with dependencies
    # Returns: [{"id": 1, "question": "...", "depends_on": []}, ...]

def build_dependency_dag(sub_questions: list) -> list:
    # Topological sort for sequential answering
```

**Example:**
```
Input: "Why is [Fe(H2O)6]2+ paramagnetic but [Fe(CN)6]4- is diamagnetic?"

Decomposed:
1. What is the oxidation state of iron in [Fe(H2O)6]2+?
2. What is the oxidation state of iron in [Fe(CN)6]4-?
3. What is the electron configuration of Fe²+?
4. How do H2O and CN- affect d-orbital splitting?
5. How does crystal field splitting influence magnetic properties?
```

**Why it matters:** Complex chemistry questions require building up from fundamentals.

### 4. LightRAG: Dual-Level Retrieval

**Source:** [HKUDS/LightRAG](https://github.com/HKUDS/LightRAG)

**What it does:** Retrieves at two levels - topic (broad) and concept (specific).

**Our implementation:**
```python
def dual_level_retrieve(query: str, top_k: int = 5):
    # Level 1: Vector search → find relevant topics
    # Level 2: Graph traversal → find concepts within topics
    return {
        "topics": [...],    # broad context
        "concepts": [...]   # specific terms
    }
```

**Why it matters:** Provides both broad context and specific details for comprehensive answers.

### 5. GraphRAG: Cross-Book Community Detection

**Source:** [Microsoft GraphRAG](https://github.com/microsoft/graphrag)

**What it does:** Detects topic communities and synthesizes perspectives across textbooks.

**Our implementation:**
```python
def detect_communities():
    # Label propagation algorithm (O(E) complexity)
    # Groups related topics into communities

def synthesize_perspectives(topic: str):
    # Retrieves excerpts from multiple textbooks
    # LLM synthesizes into coherent summary
```

**Communities detected:**
| Community | Topics | Mentions |
|-----------|--------|----------|
| Coordination Chemistry | 124 | 3,047 |
| Main Group Chemistry | 76 | 2,487 |
| Electrochemistry | 42 | 645 |
| Radiochemistry | 3 | 25 |
| Nanomaterials | 2 | 32 |
| Analytical Chemistry | 2 | 23 |

**Why it matters:** Combines multiple textbook perspectives while preserving each book's voice.

---

## Usage

### Setup

```bash
cd /storage/inorganic-chem-class
source /storage/RAG/.venv/bin/activate
```

### Build Enhanced Graph (required once)

```bash
python experiments/chemkg_rag.py --build
```

Creates `experiments/results/chemkg_enhanced.json` with mutual indexing and PageRank scores.

### Query the System

```bash
python experiments/chemkg_rag.py --query "Why do transition metals form colored compounds?"
```

Full pipeline:
1. Decomposes question (LAG)
2. For each sub-question:
   - Dual-level retrieval (LightRAG)
   - Get ranked prerequisites (HippoRAG)
   - Retrieve source chunks (KAG)
   - Generate answer
3. Synthesize final answer

### Get Prerequisites for a Topic

```bash
python experiments/chemkg_rag.py --prereqs "Crystal Field Theory"
```

Output:
```
Prerequisites for 'Crystal Field Theory':
  Molecular Orbital Theory         (PageRank: 0.0030, depth: 1)
  Atomic Structure                 (PageRank: 0.0030, depth: 2)
  Chemical Bonding                 (PageRank: 0.0029, depth: 2)
  Valence Bond Theory              (PageRank: 0.0012, depth: 2)
```

### Check Cross-Book Coverage

```bash
python experiments/chemkg_rag.py --coverage "Crystal Field Theory"
```

Output:
```
Cross-Book Coverage: Crystal Field Theory
  Total chunks: 80
  Books covered: 6
    Inorganic_Chemistry_Atkins_Shriver.pdf    28 chunks
    ic_tina.pdf                               24 chunks
    descriptive_ic.pdf                        13 chunks
    concise_ic_jd_lee.pdf                      8 chunks
```

### Synthesize Multiple Perspectives

```bash
python experiments/chemkg_rag.py --synthesize "Crystal Field Theory"
```

Retrieves excerpts from each textbook and synthesizes into comprehensive summary noting differences in approach.

### Detect Topic Communities

```bash
python experiments/chemkg_rag.py --communities
```

### Show Statistics

```bash
python experiments/chemkg_rag.py --stats
```

---

## API Reference

### ChemKGRAG Class

```python
from chemkg_rag import ChemKGRAG

rag = ChemKGRAG()
rag.load_enhanced_graph()  # or build_mutual_index() + build_prereq_graph()

# full Q&A
result = rag.answer_question("your question")
print(result["final_answer"])

# prerequisites
prereqs = rag.get_prerequisites_ranked("Crystal Field Theory", depth=2)

# PageRank scores
scores = rag.pagerank()

# cross-book
coverage = rag.get_cross_book_coverage("Coordination Chemistry")
synthesis = rag.synthesize_perspectives("Coordination Chemistry")

# communities
communities = rag.detect_communities()
```

### Key Methods

| Method | Returns | Purpose |
|--------|---------|---------|
| `build_mutual_index()` | self | Create chunk↔node mappings |
| `build_prereq_graph()` | self | Build adjacency matrix for PageRank |
| `pagerank()` | dict | Topic → centrality score |
| `get_prerequisites_ranked(topic, depth)` | list | BFS + PageRank ranking |
| `decompose_question(q)` | list | LAG sub-question extraction |
| `dual_level_retrieve(q)` | dict | Topic + concept retrieval |
| `answer_question(q)` | dict | Full pipeline |
| `detect_communities()` | dict | Label propagation clustering |
| `get_cross_book_coverage(topic)` | dict | Per-textbook chunk counts |
| `synthesize_perspectives(topic)` | str | Multi-book synthesis |

---

## Configuration

```python
# in chemkg_rag.py
QDRANT_URL = "http://localhost:6333"
COLLECTION = "textbooks_chunks"
OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen3:latest"
```

---

## Data Files

| File | Description |
|------|-------------|
| `experiments/results/knowledge_graph.json` | Original extracted graph (5,380 nodes) |
| `experiments/results/chemkg_enhanced.json` | Graph + mutual indexing + PageRank |
| `experiments/results/full_extraction_results.json` | Raw extraction with chunk mappings |

---

## Performance

| Operation | Time |
|-----------|------|
| Build mutual index | ~5 seconds |
| Build PageRank | ~2 seconds |
| Single query (5 sub-questions) | ~60-90 seconds |
| Community detection | <1 second |
| Cross-book synthesis | ~30 seconds |

---

## Limitations

1. **No multimodal support** - Chemical structure diagrams not indexed (planned for v2)
2. **LLM latency** - Each sub-question requires LLM call
3. **English only** - Textbooks and queries in English

---

## References

1. KAG: https://github.com/OpenSPG/KAG
2. HippoRAG: https://github.com/OSU-NLP-Group/HippoRAG
3. LAG: https://arxiv.org/abs/2411.14012
4. LightRAG: https://github.com/HKUDS/LightRAG
5. GraphRAG: https://github.com/microsoft/graphrag

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-18 | Initial implementation with 5 components |

---

*Part of the Knowledge Graph Pedagogy Project*
*McNeese State University, CHEM 361*
