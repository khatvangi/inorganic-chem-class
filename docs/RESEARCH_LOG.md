# Research Log: Knowledge Graph Pedagogy Project

**Project:** Bottom-Up Curriculum Design via Textbook Knowledge Extraction
**Subject:** CHEM 361 Inorganic Chemistry
**Location:** McNeese State University

---

## 2026-01-18 (Session 1)

### Context
Starting from a broken `context_graph.json` (170 disconnected components, garbage nodes). Previous approach used random sampling of 60 chunks per book from first 100 only - insufficient coverage.

### Key Decisions Made

**Decision 1: Bottom-Up vs Top-Down**
- User explicitly rejected curriculum-driven extraction
- Quote: "NO it is the other way round. bottom up approach data should tell me how to redesign curriculum"
- Rationale: Traditional syllabi reflect instructor bias, not intrinsic knowledge structure

**Decision 2: Dendrimer Structure**
- Not linear chapter progression
- Multiple threads from core concepts (orbitals) to all derived properties
- Like Feynman lectures - everything traces back to fundamentals

**Decision 3: Preserve Textbook Voices**
- User: "not mushy... each textbook has unique style"
- Atkins = succinct, theoretical
- JD Lee = foundational
- Descriptive = narrative
- Goal: Synthesize without homogenizing

**Decision 4: Three-Level Granularity**
- Topic (chapter): "Coordination Chemistry"
- Subtopic (section): "Crystal Field Splitting"
- Concept (term): "Δo", "CFSE"
- Tested on 100 chunks, confirmed useful hierarchy

**Decision 5: LLM Selection**
- Qwen3 for STEM extraction (strong chemistry knowledge)
- Mistral pulled for validation (multi-LLM consensus planned)
- Temperature 0.1 for deterministic outputs

### Technical Implementation

**Normalization Rules Created:**
```python
# 50+ topic mappings
"coordination compounds" → "Coordination Chemistry"
"solid-state chemistry" → "Solid State Chemistry"

# Garbage filtering
GARBAGE_TOPICS = {"inorganic chemistry", "textbook introduction", ...}
```

**Extraction Prompt (final version):**
```
Analyze this inorganic chemistry textbook passage and extract knowledge at THREE levels:
1. TOPIC: Main chapter-level subject
2. SUBTOPIC: Section-level subject
3. KEY_CONCEPTS: 3-5 specific terms
4. PREREQUISITES: What must student already know?
5. LEADS_TO: What does this enable?
```

### Results

**Extraction Statistics:**
- Input: 7,726 chunks from 6 textbooks
- Runtime: ~4 hours (single GPU)
- Output: 5,337 nodes, 2,885 edges

**Topic Distribution:**
1. Main Group Chemistry: 1,567 (20.3%)
2. Coordination Chemistry: 1,045 (13.5%)
3. Solid State Chemistry: 418 (5.4%)

**Observation:** Main Group dominates because descriptive textbooks cover all elements. Coordination Chemistry expected to be more central in advanced texts.

### New Textbook Added
- `descriptive_ic_house.pdf` ingested: 1,027 chunks
- User likes: "highlight boxes, clear presentation"
- Separate extraction running (completed ~80% by session end)

### Artifacts Created

| File | Size | Purpose |
|------|------|---------|
| `experiments/normalizer.py` | 4KB | Canonicalization rules |
| `experiments/full_extraction.py` | 8KB | Main pipeline |
| `experiments/analyze_textbooks.py` | 6KB | Style analysis |
| `experiments/extract_house.py` | 5KB | House-specific extraction |
| `attendance.html` + `attendance.js` | 36KB | QR attendance system |
| `topics.html` + `topics.js` | 28KB | Knowledge graph explorer |
| `data/schedule.json` | 5KB | 30 class sessions |
| `experiments/results/knowledge_graph.json` | 1.4MB | Final graph |

### User Feedback Recorded
- "we need useful granularity... topic/subtopic not words"
- "core should emerge ideally"
- "Feynman lectures... single (multiple) threads pass through from orbitals to all properties"
- "preserve each textbook's unique style"

### Open Questions
1. How to handle topics that appear in multiple textbooks with different emphasis?
2. What's the optimal graph layout for 974 topics?
3. How to measure "centrality" of a concept in chemistry curriculum?
4. Can prerequisite chains predict student difficulty?

### Next Steps
1. Complete House extraction
2. Run textbook style analysis
3. Merge House into main graph
4. Graph connectivity analysis
5. Begin curriculum optimization

---

## 2026-01-18 (Session 2)

### Context
Continuing from Session 1. House extraction complete (531 results), merged into main graph (5,380 nodes total). Topics.js integrated with real knowledge graph data.

### Key Decisions Made

**Decision 6: Enhanced Textbook Analysis**
- Expanded from 4 to 9 analysis dimensions
- Added: Explanation Depth, Problem-Solving Pedagogy, Real-World Connections, Historical Context, Readability Metrics
- Flesch Reading Ease provides quantitative comparability

**Decision 7: Graph-Enhanced RAG Research**
- Surveyed 8 major frameworks: GraphRAG, LightRAG, HippoRAG, KAG, LAG, RAPTOR, MMGraphRAG, mKG-RAG
- Key insight: Our knowledge graph already has prerequisite chains - we're halfway to advanced reasoning
- Critical gap identified: No mutual indexing between chunks and graph nodes

### Technical Implementation

**Textbook Analysis Results (7 books × 9 dimensions):**

| Book | Flesch Score | Difficulty | Best For |
|------|--------------|------------|----------|
| Atkins/Shriver | 36.4 | Advanced | Deep coordination chemistry |
| ic_tina | 35.3 | Intermediate | Main group, MOFs |
| descriptive_ic | 38.6 | Intermediate | Applications |
| House | 48.8 | Intermediate | Clear introduction |
| JD Lee | 51.2 | Intermediate | Foundational concepts |
| Basset | 30.5 | Intermediate | Industrial applications |
| Advanced IC | 41.9 | Advanced | Reaction mechanisms |

**Key Finding:** JD Lee most readable (51.2), House second (48.8). All texts "fairly difficult" by Flesch standards - appropriate for undergraduate STEM.

### RAG Framework Survey

Documented in `docs/RAG_LANDSCAPE.md`. Key frameworks compared:

| Framework | Innovation | Cost | Best For |
|-----------|------------|------|----------|
| KAG | Mutual KG-chunk indexing | Medium | Professional domains |
| LAG | LLM as Continuous KG | Medium | Tacit knowledge |
| HippoRAG | Personalized PageRank | Low | Multi-hop Q&A |
| LightRAG | Dual-level retrieval | Low | Fast graph reasoning |
| GraphRAG | Community summaries | High | Narrative synthesis |

**Proposed Hybrid: ChemKG-RAG**
- FROM KAG: Mutual indexing (chunk ↔ node)
- FROM LAG: Sub-question decomposition
- FROM HippoRAG: PageRank on prerequisites
- FROM LightRAG: Dual-level retrieval

### Results

**Textbook Analysis Output:**
- File: `experiments/results/textbook_analysis.json`
- 7 textbooks analyzed
- 9 dimensions per book
- Quantitative + qualitative metrics

**Documentation Created:**
- `docs/RAG_LANDSCAPE.md` - Comprehensive framework survey (400+ lines)

### User Feedback
- "lets look at this see does it enhance our work" (on KAG article)
- "we also have graphrag, multimodal graphs, lets put all available tool knowledge out here"
- "first save what you just wrote"

### Open Questions
1. Which RAG framework to implement first? (Recommend: KAG mutual indexing)
2. How to integrate PageRank with our prerequisite graph?
3. Should we add multimodal support for chemical structure diagrams?
4. Can we use cross-textbook community detection to find consensus topics?

### Next Steps
1. ~~Implement mutual indexing (link graph nodes to source chunk IDs)~~ ✓
2. ~~Add PageRank-based prerequisite traversal~~ ✓
3. ~~Build Q&A interface using hybrid approach~~ ✓
4. ~~Consider LightRAG or HippoRAG for fast prototyping~~ ✓

---

## 2026-01-18 (Session 3)

### Context
Implementing ChemKG-RAG hybrid framework as specified in RAG_LANDSCAPE.md. All four core components plus cross-book synthesis.

### Key Decisions Made

**Decision 8: Hybrid Architecture**
- Combined 5 frameworks into single `chemkg_rag.py`:
  - KAG: Mutual indexing (chunk ↔ node bidirectional)
  - HippoRAG: PageRank on prerequisite graph
  - LAG: Sub-question decomposition with dependency DAG
  - LightRAG: Dual-level retrieval (topic + concept)
  - GraphRAG: Label propagation community detection

**Decision 9: Fast Community Detection**
- Replaced O(n³) modularity optimization with O(E) label propagation
- Converges in 4 iterations, finds 6 meaningful communities

**Decision 10: Cross-Book Synthesis**
- Each topic tracked across all 6-7 textbooks
- Synthesis preserves each book's voice while combining perspectives

### Technical Implementation

**ChemKG-RAG Components:**

```python
# 1. KAG Mutual Indexing
node_to_chunks: 5,339 nodes → 7,715 chunks
chunk_to_nodes: 7,715 chunks → nodes
avg chunks/node: 5.8

# 2. HippoRAG PageRank
1,017 topic nodes
1,458 prerequisite edges
712 leads-to edges
Top fundamental: Main Group Chemistry, Periodic Trends, Redox Chemistry

# 3. LAG Decomposition
Complex question → atomic sub-questions
Dependency DAG with topological sort
Sequential answering with context passing

# 4. LightRAG Dual-Level
Level 1: Topic retrieval via vector search
Level 2: Concept retrieval from top topics

# 5. GraphRAG Communities
6 communities detected:
- Coordination Chemistry (124 topics)
- Main Group Chemistry (76 topics)
- Electrochemistry (42 topics)
- Radiochemistry (3 topics)
- Nanomaterials (2 topics)
- Analytical Chemistry (2 topics)
```

**CLI Interface:**
```bash
# build enhanced graph
python experiments/chemkg_rag.py --build

# query with full pipeline
python experiments/chemkg_rag.py --query "Why is [Fe(H2O)6]2+ paramagnetic?"

# get prerequisites
python experiments/chemkg_rag.py --prereqs "Crystal Field Theory"

# cross-book coverage
python experiments/chemkg_rag.py --coverage "Crystal Field Theory"

# synthesize perspectives
python experiments/chemkg_rag.py --synthesize "Crystal Field Theory"

# community detection
python experiments/chemkg_rag.py --communities
```

### Results

**Query Test:**
Input: "Why is [Fe(H2O)6]2+ paramagnetic but [Fe(CN)6]4- is diamagnetic?"

Pipeline:
1. LAG decomposed into 5 sub-questions (oxidation state, electron config, ligand effects, etc.)
2. Each sub-question: retrieved topics, concepts, prerequisites, source chunks
3. Generated answers with full context
4. Synthesized into comprehensive final answer

Output: Accurate explanation of high-spin vs low-spin, weak-field vs strong-field ligands, crystal field splitting effects.

**Cross-Book Synthesis Test:**
Topic: Crystal Field Theory
Coverage: 80 chunks across 6 books
- Atkins/Shriver: 28 chunks (theoretical, Racah parameters)
- ic_tina: 24 chunks (LFSE, thermodynamic applications)
- Others: complementary perspectives

### Artifacts Created

| File | Size | Purpose |
|------|------|---------|
| `experiments/chemkg_rag.py` | 30KB | Full hybrid RAG implementation |
| `experiments/results/chemkg_enhanced.json` | ~2MB | Graph with mutual indexing + PageRank |

### User Feedback
- "lets cook a gumbo like never before" (enthusiasm for JCE paper)
- Wants comprehensive documentation for publication

### Open Questions
1. How to integrate with topics.html visualization?
2. Should we add a web interface for ChemKG-RAG?
3. MMGraphRAG (multimodal) deferred to v2 - how to add chemical structure images?

### Next Steps
1. Update topics.html to use ChemKG-RAG for query panel
2. Add interactive Q&A to web interface
3. Document methodology for JCE paper
4. Begin v2 planning (multimodal)

---

## Template for Future Entries

```markdown
## YYYY-MM-DD (Session N)

### Context
[What was the state before this session?]

### Key Decisions Made
[Important choices with rationale]

### Technical Implementation
[Code, prompts, parameters]

### Results
[Numbers, observations]

### User Feedback
[Direct quotes when possible]

### Open Questions
[Unresolved issues]

### Next Steps
[Planned work]
```

---

## 2026-01-18 (Session 4)

### Context
ChemKG-RAG implemented and documented. Now using the knowledge graph to generate data-driven curriculum recommendations and compare with existing CHEM 361 syllabus.

### Key Decisions Made

**Decision 11: 8 Curriculum Generation Methods**
Implemented multiple ordering strategies to compare approaches:
1. Topological Sort - prerequisite order (Kahn's algorithm)
2. PageRank - fundamentals first (power iteration)
3. Hybrid - PageRank weighted, prerequisite constrained
4. Coverage - textbook emphasis (mention count)
5. Depth-First - deep dive into branches
6. Breadth-First - broad foundation first
7. Community-Based - cluster related topics (label propagation)
8. Difficulty - simpler topics first (prereq count)

**Decision 12: Unit Reordering Recommendation**
Data analysis revealed a significant finding:
- **Existing order:** Coordination → Main Group → Solid State
- **Data suggests:** Main Group → Coordination → Solid State
- **Rationale:** Main Group has highest PageRank (most foundational) and highest coverage (43%)

### Technical Implementation

**Curriculum Generator:**
```python
class CurriculumGenerator:
    # 8 methods for curriculum ordering
    # Exports to JSON with topic metadata
    # Compares methods side-by-side
```

**Key Metrics Extracted:**
| Unit | PageRank | Coverage | Existing Sessions |
|------|----------|----------|-------------------|
| Main Group | 0.0432 | 40% (1937) | 7 |
| Coordination | 0.0132 | 43% (2073) | 9 |
| Solid State | 0.0069 | 17% (809) | 7 |

### Results

**Major Finding:**
The knowledge graph suggests Main Group should be taught FIRST because:
1. Highest PageRank = most foundational concepts
2. Periodic trends are prerequisites for coordination chemistry
3. Crystal Field Theory depends on atomic structure concepts

**Session Allocation (Data-Driven):**
- Main Group: 9 sessions (currently 7) → +2
- Coordination: 10 sessions (currently 9) → +1
- Solid State: 4 sessions (currently 7) → -3

**67 significant topics identified** (mention count >= 10), mapped to 23 teaching sessions.

### Artifacts Created

| File | Purpose |
|------|---------|
| `experiments/curriculum_generator.py` | 8 ordering methods |
| `experiments/results/recommended_curriculum.json` | Breadth-first curriculum |
| `experiments/results/curriculum_comparison.json` | Existing vs data-driven |

### User Feedback
- "yes generate the curriculum, both 1 and 2 topological and pagerank and lets think about what other options we can muster"

### Open Questions
1. Should the course actually be reordered? Pedagogical vs practical constraints
2. How to handle "Main Group Chemistry" being too broad - need subtopics?
3. Can we map specific topics to specific SLOs?
4. How does this compare to other institutions' curricula?

### Next Steps
1. Present findings to user for pedagogical validation
2. Create detailed session-by-session mapping
3. Compare with ACS guidelines for inorganic chemistry
4. Document methodology for JCE paper

---

## 2026-01-18 (Session 5)

### Context
After generating curriculum comparisons, user had a breakthrough insight about knowledge organization that fundamentally changes how we should think about prerequisites and curriculum structure.

### Key Insight: Hierarchical Knowledge Forest

**The Problem (User's Words):**
> "Instead of a 2D graph, we need to look at hierarchical conceptual evolution. Although a building has bricks and bricks have atoms and atoms have electrons, this does not help. After bricks we have different hierarchy. Understanding building should stop at bricks, understanding bricks should stop at meso, and understanding meso to nano to atoms. A blind path by definition leads to electrons."

**The Solution:** Knowledge exists at multiple SCALES, and each scale contains TREES of related concepts. Not everything needs to trace back to quantum mechanics.

### The Four Scales Model

```
SCALE 4: QUANTUM     - Wave functions, orbitals, spin
SCALE 3: ELECTRONIC  - Crystal Field Theory, MO diagrams, bonding
SCALE 2: STRUCTURAL  - Coordination geometry, crystal structures, isomers
SCALE 1: DESCRIPTIVE - Periodic trends, element properties, reactions
```

**Key Principle:** Stay within scale when possible. Only "escalate" to deeper scale when explanation requires it.

### Trees Within Scales

Each scale is not flat but contains multiple trees:

- DESCRIPTIVE: Main Group tree, Transition Metal tree, Periodic Trends tree
- STRUCTURAL: Coordination tree, Crystal Structure tree, Symmetry tree
- ELECTRONIC: CFT tree, MO Theory tree, Bonding tree
- QUANTUM: Atomic Structure tree, Quantum Mechanics tree

### Navigation Rules

1. **Stay within scale** when learning objective allows
2. **Explore tree siblings** before escalating to deeper scale
3. **Escalate only for "why"** questions that require deeper explanation
4. **Blind path** (all the way to quantum) only for anomalies

### Validation from Data

Cross-scale prerequisite analysis confirmed:
- Most edges stay within scale (self-referential)
- QUANTUM → ELECTRONIC flow (16 edges) confirms escalation path
- DESCRIPTIVE most self-contained (30 internal edges)
- Some topics are "endpoints" that don't require deeper understanding

### Implications for Curriculum

| Old Approach | New Approach |
|--------------|--------------|
| Flat prerequisite chain | Multi-scale forest |
| Everything traces to fundamentals | Stop at appropriate scale |
| Single ordering algorithm | Per-scale + cross-scale ordering |
| "Prerequisite" = all-or-nothing | "Escalation" = as-needed |

### Examples

| Learning Objective | Required Scale | No Deeper Needed |
|-------------------|----------------|------------------|
| Name a coordination complex | STRUCTURAL | ✓ |
| Explain why [Cu(H2O)6]²⁺ is blue | ELECTRONIC | ✓ |
| Explain relativistic effects in Au | QUANTUM | (endpoint) |
| List alkali metal properties | DESCRIPTIVE | ✓ |

### Artifacts Created

| File | Purpose |
|------|---------|
| `docs/HIERARCHICAL_KNOWLEDGE_MODEL.md` | Full documentation of insight |

### User Feedback
- "within each scale we have trees"
- "a blind path by definition leads to electrons"
- "record all this in detail before we drift"

### Open Questions
1. How to automatically tag 5,380 nodes with scale membership?
2. How to detect tree structure within each scale?
3. How does this map to Bloom's taxonomy?
4. Can we quantify "escalation cost" between scales?

### Next Steps
1. ~~Document the hierarchical model~~ ✓
2. Implement scale-aware curriculum generator
3. Tag existing topics with scale membership
4. Create escalation map for cross-scale transitions
5. Validate against SLOs

---

## VISION: Meta-Scale Knowledge Forest

**Documented:** 2026-01-18 (end of Session 5)

### The Grand Vision

Expand the methodology to ALL undergraduate chemistry:

```
100 level: General Chemistry (foundation for all)
200 level: Organic I, Quantitative Analysis
300 level: Organic II, PChem, Inorganic, Analytical, Biochem
400 level: Advanced courses per branch
```

### Branch-Specific Scale Models (Planned)

| Branch | Scale Hierarchy |
|--------|-----------------|
| Inorganic | Quantum → Electronic → Structural → Descriptive ✓ |
| Organic | Orbital → Mechanistic → Functional → Synthetic |
| Physical | Quantum → Statistical → Kinetic → Thermodynamic |
| Analytical | Signal → Instrumental → Methodological → Practical |
| Biochemistry | Molecular → Structural → Functional → Systems |
| Materials | Atomic → Nano → Micro → Bulk |

### Meta-Scale-Tree Goal

Unified knowledge forest showing how ALL branches connect at appropriate scales.

**Applications:**
- Design entire degree programs (not just single courses)
- Identify prerequisite gaps between courses
- Advise transfer students
- Compare textbook coverage across publishers
- Align with ACS guidelines

### Data Collection Plan

- 30+ textbooks across all branches
- 50,000+ chunks
- 5,000+ topics
- 500+ cross-branch edges

**Full vision document:** `~/.claude/CHEMKG_VISION.md`

---

## 2026-01-18 (Session 6)

### Context
User decided to adopt data-driven curriculum order. "We go by data, that is the point."

### Decision Made

**APPROVED:** Reorder CHEM 361 curriculum based on knowledge graph analysis.

```
OLD: Coordination → Main Group → Solid State
NEW: Main Group → Coordination → Solid State
```

### Rationale

1. Main Group has highest PageRank (0.0432) = most foundational
2. Periodic trends are prerequisites for Crystal Field Theory
3. 40% of textbook coverage is Main Group fundamentals
4. Students need electron configuration before CFT d-orbital splitting

### New Curriculum Structure

| Unit | Topic | Sessions | Scale |
|------|-------|----------|-------|
| 1 | Main Group Chemistry | 9 | DESCRIPTIVE |
| 2 | Coordination Chemistry | 8 | STRUCTURAL → ELECTRONIC |
| 3 | Solid State Chemistry | 5 | STRUCTURAL + ELECTRONIC |

### Scale Tagging

Every lecture now tagged with its primary scale level:
- DESCRIPTIVE: 13 lectures (properties, trends)
- STRUCTURAL: 6 lectures (geometry, isomers)
- ELECTRONIC: 6 lectures (CFT, band theory)

### Student Learning Tracking

Created schema to track:
- Pretest (baseline Gen Chem knowledge)
- Quiz scores by scale level
- Exam scores (cross-unit transfer)
- Scale difficulty comparison
- Prerequisite effectiveness correlation

### Artifacts Created

| File | Purpose |
|------|---------|
| `data/schedule_data_driven.json` | New curriculum |
| `data/student_tracking_schema.json` | Learning progress tracking |
| `docs/CURRICULUM_DECISION.md` | Decision documentation |

### User Feedback
- "nope, we go by data, that is the point"
- "record chemistry students input and their learning progress"

### Research Questions to Answer

1. Does Main Group first improve CFT understanding?
2. Which scale level is most challenging?
3. Do students show better cross-unit transfer?
4. Where do prerequisite gaps manifest?

### Next Steps

1. ~~Create data-driven curriculum~~ ✓
2. ~~Create student tracking schema~~ ✓
3. Build pretest instrument for periodic trends
4. Tag quiz/exam questions by scale level
5. Collect data Spring 2025 semester
6. Analyze and publish findings (JCE paper)

---

*Log maintained by: Claude Code*
*Review frequency: End of each work session*
