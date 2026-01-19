# Knowledge Graph Pedagogy: A Bottom-Up Approach to Curriculum Design

**Project:** CHEM 361 Inorganic Chemistry Knowledge Graph
**Institution:** McNeese State University
**Principal Investigator:** Kiran Boggavarapu
**Date Started:** January 18, 2026
**Status:** Active Development

---

## Abstract

This project develops a methodology for extracting the implicit knowledge structure from multiple textbooks to create a unified, navigable knowledge graph. Unlike traditional top-down curriculum design (syllabus → topics), we employ a **bottom-up, data-driven approach** where the curriculum structure **emerges from the textbooks themselves**.

The goal is not to create a "mushy blend" of textbooks, but to preserve each book's unique pedagogical voice while mapping the conceptual landscape they collectively describe.

---

## 1. Problem Statement

### Traditional Curriculum Design Limitations
1. **Top-down bias**: Instructor decides topics based on personal expertise/preference
2. **Textbook mismatch**: Syllabus may not align with available textbook coverage
3. **Hidden prerequisites**: Conceptual dependencies often implicit, not explicit
4. **Lost context**: Students miss connections between topics across chapters
5. **Single-source dependency**: One textbook's perspective dominates

### Our Approach
- Let the **data tell us** how to structure the curriculum
- Extract topics, concepts, and relationships from **multiple textbooks**
- Build a **dendrimer-like structure** (branched, not linear) with logical trace-back to core concepts
- Preserve each textbook's **unique presentation style**
- Enable **Feynman-style threads** from fundamental concepts to all derived properties

---

## 2. Data Sources

### Textbook Corpus (8,756 chunks total)

| Textbook | Chunks | Characteristics |
|----------|--------|-----------------|
| Atkins/Shriver Inorganic Chemistry | 2,494 | Authoritative, comprehensive, theoretical |
| ic_tina.pdf | 2,375 | Detailed coverage, systematic |
| Descriptive Inorganic Chemistry (Rodgers) | 1,495 | Narrative style, applications |
| Descriptive IC (House) | 1,027 | Highlight boxes, clear presentation |
| Concise IC (JD Lee) | 565 | Foundational, undergraduate-focused |
| IC Basset | 446 | Applications, industrial focus |
| Advanced IC Applications | 351 | Specialized topics |

### Chunking Strategy
- **Chunk size:** 2,000 characters (with overlap)
- **Embedding model:** nomic-embed-text (768 dimensions)
- **Storage:** Qdrant vector database
- **Collection:** `textbooks_chunks`

---

## 3. Methodology

### Phase 1: Granularity Experiment (Completed)
**Goal:** Determine optimal extraction granularity

Tested three levels:
1. **Topic** (chapter-level): "Coordination Chemistry", "Crystal Field Theory"
2. **Subtopic** (section-level): "Octahedral Complexes", "Jahn-Teller Distortion"
3. **Concept** (term-level): "d-orbital splitting", "CFSE"

**Result:** Three-level hierarchy works well. Topics provide navigable structure, subtopics add specificity, concepts enable precise retrieval.

### Phase 2: Normalization Layer (Completed)
**Goal:** Canonicalize extracted entities

**Challenges:**
- Same concept, different names: "Coordination Compounds" vs "Coordination Chemistry"
- Garbage extractions: "Inorganic Chemistry", "Textbook Introduction"
- Case variations: "crystal field theory" vs "Crystal Field Theory"

**Solution:** `normalizer.py` with:
```python
TOPIC_MAPPINGS = {
    "coordination compounds": "Coordination Chemistry",
    "solid state chemistry": "Solid State Chemistry",
    "solid-state chemistry": "Solid State Chemistry",
    # ... 50+ mappings
}

GARBAGE_TOPICS = {
    "inorganic chemistry", "textbook introduction",
    "general chemistry", "chapter summary", ...
}
```

**Validation:** 45 raw topics → 21 normalized (target: 15-25) ✓

### Phase 3: Full Extraction (Completed)
**Goal:** Extract knowledge from all 7,726 chunks

**Pipeline:**
1. Query Qdrant for all chunks
2. For each chunk, prompt LLM:
   ```
   Extract:
   1. TOPIC: Main chapter-level subject
   2. SUBTOPIC: Section-level subject
   3. KEY_CONCEPTS: 3-5 specific terms
   4. PREREQUISITES: What must student already know?
   5. LEADS_TO: What does this enable?
   ```
3. Normalize extraction
4. Build graph (nodes + edges)
5. Save progress every 50 chunks (resumable)

**LLM Used:** Qwen3 (8B parameters, local via Ollama)
- Temperature: 0.1 (deterministic)
- Context: 4096 tokens
- Prompt includes `/no_think` for direct responses

**Runtime:** ~4 hours on single GPU (RTX 4080)

### Phase 4: Graph Construction (Completed)
**Goal:** Build navigable knowledge graph

**Node Types:**
- `topic`: Chapter-level subjects (974 unique)
- `concept`: Specific terms/ideas (189 unique)
- `prerequisite`: Required prior knowledge (4,174 unique)

**Edge Types:**
- `contains`: Topic → Concept relationship
- `prerequisite_for`: Prerequisite → Topic dependency
- `leads_to`: Topic → Topic progression

**Final Graph:**
- **Nodes:** 5,337
- **Edges:** 2,885
- **Connected components:** Analysis pending

---

## 4. Key Findings

### Topic Distribution (Top 15)
| Rank | Topic | Mentions | % of Corpus |
|------|-------|----------|-------------|
| 1 | Main Group Chemistry | 1,567 | 20.3% |
| 2 | Coordination Chemistry | 1,045 | 13.5% |
| 3 | Solid State Chemistry | 418 | 5.4% |
| 4 | Electrochemistry | 252 | 3.3% |
| 5 | Acid-Base Chemistry | 166 | 2.1% |
| 6 | Bioinorganic Chemistry | 166 | 2.1% |
| 7 | Crystal Field Theory | 165 | 2.1% |
| 8 | Molecular Orbital Theory | 140 | 1.8% |
| 9 | Chemical Bonding | 112 | 1.5% |
| 10 | Organometallic Chemistry | 91 | 1.2% |

### Prerequisite Hubs (Most Required)
- Electron Configuration
- Atomic Structure
- Oxidation States
- Periodic Trends

### Destination Topics (Most "Led To")
- Crystal Field Theory
- Coordination Chemistry
- Spectroscopy
- Applications/Catalysis

---

## 5. Textbook Style Analysis (Pending)

**Goal:** Characterize each textbook's pedagogical approach

Dimensions to analyze:
1. **Teaching Philosophy**: Theoretical-first vs example-driven vs applications-focused
2. **Difficulty Level**: Introductory / Intermediate / Advanced
3. **Writing Tone**: Formal / Conversational / Technical
4. **Use of Visuals**: Diagram density, integration quality
5. **Mathematical Rigor**: Qualitative / Semi-quantitative / Highly quantitative
6. **Strengths/Weaknesses**: Topic coverage, clarity, depth

**Script:** `experiments/analyze_textbooks.py` (ready to run)

---

## 6. Applications

### 6.1 Topic Explorer (Implemented)
Interactive D3.js visualization at `topics.html`:
- Force-directed graph of topic relationships
- Click topic → see prerequisites, leads-to, concepts
- Search and filter topics
- Zoom/pan navigation

### 6.2 Curriculum Redesign (Planned)
Use graph to:
- Identify optimal topic ordering (topological sort on prerequisites)
- Find gaps in current syllabus
- Suggest prerequisite reviews before new topics
- Create multiple learning paths for different student backgrounds

### 6.3 Adaptive Learning (Planned)
- Track student mastery per topic
- Recommend remediation based on prerequisite gaps
- Generate topic-specific quizzes from knowledge graph

### 6.4 Cross-Textbook Synthesis (Planned)
For any topic, retrieve and display:
- Atkins' rigorous theoretical treatment
- JD Lee's foundational explanation
- House's clear presentation with highlights
- Rodgers' narrative with applications

---

## 7. Reproducibility

### Requirements
```
Python 3.10+
Qdrant (localhost:6333)
Ollama with qwen3:latest
~16GB GPU memory
```

### Steps to Reproduce
```bash
# 1. Ingest textbooks
cd /storage/ragstack
./ingest_all.sh textbooks

# 2. Run extraction
cd /storage/inorganic-chem-class
source /storage/RAG/.venv/bin/activate
python experiments/full_extraction.py

# 3. Analyze textbooks
python experiments/analyze_textbooks.py

# 4. View results
python -m http.server 8080
# visit http://localhost:8080/topics.html
```

### Key Files
| File | Purpose |
|------|---------|
| `experiments/normalizer.py` | Topic canonicalization rules |
| `experiments/full_extraction.py` | Main extraction pipeline |
| `experiments/analyze_textbooks.py` | Textbook style analysis |
| `experiments/results/knowledge_graph.json` | Final graph (1.4MB) |
| `experiments/results/textbook_analysis.json` | Style analysis (pending) |

---

## 8. Future Work

### Short-term
- [ ] Complete textbook style analysis
- [ ] Merge House extraction into main graph
- [ ] Multi-LLM validation (Qwen + Mistral consensus)
- [ ] Graph connectivity analysis

### Medium-term
- [ ] Extend to Physical Chemistry, Organic Chemistry
- [ ] Cross-course prerequisite mapping
- [ ] Student learning path optimization
- [ ] Integration with LMS (Moodle)

### Long-term
- [ ] Publish methodology paper
- [ ] Open-source toolkit for other institutions
- [ ] AI tutor using knowledge graph + RAG

---

## 9. References

1. Feynman, R. P. (1965). The Feynman Lectures on Physics.
2. Novak, J. D., & Cañas, A. J. (2008). The theory underlying concept maps.
3. Chi, M. T. H. (2009). Active-Constructive-Interactive: A framework for differentiating learning activities.

---

## 10. Changelog

| Date | Change |
|------|--------|
| 2026-01-18 | Initial methodology document |
| 2026-01-18 | Full extraction complete (7,726 chunks → 5,337 nodes) |
| 2026-01-18 | House textbook added (1,027 chunks) |
| 2026-01-18 | Topic explorer integrated with knowledge graph |

---

*Document maintained by: Claude Code + Kiran Boggavarapu*
