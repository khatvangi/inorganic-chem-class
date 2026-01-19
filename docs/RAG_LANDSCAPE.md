# Graph-Enhanced RAG Landscape (2024-2025)

**Purpose:** Comprehensive survey of graph-based RAG frameworks for potential integration with our knowledge graph project.
**Last Updated:** 2026-01-18
**Research By:** Claude Code + Kiran Boggavarapu

---

## Executive Summary

The RAG evolution: Vector RAG (2023) → GraphRAG (2024) → KAG/LAG/HippoRAG (2025). Each generation addresses the previous one's weakness: vectors lack structure → graphs add structure but are expensive → newer frameworks optimize for cost/speed while preserving reasoning.

---

## 1. Master Comparison Table

| Framework | Core Innovation | Graph Type | Reasoning | Cost | Speed | Best For |
|-----------|----------------|------------|-----------|------|-------|----------|
| **Vanilla RAG** | Vector similarity | None | None | Low | Fast | Simple Q&A |
| **GraphRAG** (Microsoft) | Community summaries | Entity-relation | Global + Local | High | Slow | Complex narratives |
| **LightRAG** | Dual-level retrieval | Entity-relation | Low + High level | Low | Fast | Balanced performance |
| **HippoRAG** | Hippocampal memory | Personalized PageRank | Associative | Low | Fast | Multi-hop Q&A |
| **KAG** (Ant Group) | Mutual KG-chunk indexing | Semantic KG | Logical form-guided | Medium | Medium | Professional domains |
| **LAG** | LLM as Continuous KG | Semantic KG + axioms | Dependency decomposition | Medium | Medium | Tacit knowledge |
| **RAPTOR** | Hierarchical summaries | Tree structure | Multi-level abstraction | Low | Fast | Long documents |
| **MMGraphRAG** | Cross-modal fusion | Multimodal KG | Scene graph + text KG | High | Slow | Vision + Language |

---

## 2. Framework Details

### 2.1 GraphRAG (Microsoft)

**Repository:** https://github.com/microsoft/graphrag
**Documentation:** https://microsoft.github.io/graphrag/

**How it works:**
- Uses LLM to extract entities and relationships from text chunks
- Builds knowledge graph from extracted information
- Applies community detection algorithm to find topic clusters
- Creates hierarchical summaries at community level
- Queries use both local (entity-specific) and global (community summary) retrieval

**Key innovation:** Community summaries enable "big picture" synthesis across documents.

**Limitations:** High token cost (10-50x vanilla RAG), slow indexing.

### 2.2 LightRAG

**Repository:** https://github.com/HKUDS/LightRAG
**Paper:** https://arxiv.org/abs/2410.05779 (EMNLP 2025)

**How it works:**
- Extracts entities and relations like GraphRAG
- Uses dual-level retrieval: low-level (specific entities) + high-level (abstract concepts)
- Retrieves via vectors directly, uses graph only for structural context
- Incremental updates: add new nodes/edges without rebuilding entire index

**Key innovation:** Avoids community traversal entirely - dramatically cheaper and faster.

**Recent updates (2025):**
- Citation functionality for source attribution
- MongoDB, PostgreSQL support
- VideoRAG for long-context videos
- MiniRAG for small models

### 2.3 HippoRAG

**Repository:** https://github.com/OSU-NLP-Group/HippoRAG
**Paper:** NeurIPS 2024

**How it works:**
- Inspired by hippocampal indexing theory of human long-term memory
- Orchestrates LLMs, knowledge graphs, and Personalized PageRank
- Mimics neocortex (pattern recognition) and hippocampus (associative memory)
- Single-step retrieval achieves iterative retrieval performance

**Key innovation:** Personalized PageRank enables associative retrieval like human memory.

**Performance:**
- Outperforms SOTA by up to 20% on multi-hop QA
- 10-20x cheaper than iterative retrieval methods
- 6-13x faster than IRCoT

**HippoRAG 2 (2025):**
- 7% improvement in associative memory tasks
- Fewer resources for offline indexing than GraphRAG, RAPTOR, LightRAG

### 2.4 KAG (Knowledge Augmented Generation)

**Repository:** https://github.com/OpenSPG/KAG
**Paper:** https://arxiv.org/abs/2409.13731

**How it works:**
Five key enhancements:
1. **LLM-friendly knowledge representation** - DIKW hierarchy
2. **Mutual-indexing** - bidirectional links between KG nodes and text chunks
3. **Logical-form-guided reasoning** - structured query planning
4. **Knowledge alignment** - semantic consistency across sources
5. **Model capability enhancement** - KAG-specific LLM improvements

**Key innovation:** Mutual indexing enables both graph traversal AND chunk retrieval from same query.

**Performance:**
- 19.6% improvement on 2wiki (F1)
- 33.5% improvement on HotpotQA (F1)
- Deployed in Ant Group's E-Government and E-Health Q&A

**Architecture components:**
- `kg-builder`: Constructs LLM-friendly knowledge representations
- `kg-solver`: Logical reasoning engine with planning, reasoning, retrieval operators
- `kag-model`: Model layer (future release)

### 2.5 LAG (Logic Augmented Generation)

**Paper:** https://arxiv.org/abs/2411.14012
**ScienceDirect:** https://www.sciencedirect.com/science/article/pii/S1570826824000453

**Core concept:**
- LLMs as "Reactive Continuous Knowledge Graphs" - generate infinite relations on-demand
- SKGs provide "discrete heuristic dimension" with logical and factual boundaries
- Combines tacit knowledge (LLM) with explicit knowledge (SKG)

**How it works:**
1. **Dependency-aware decomposition** - break complex questions into atomic sub-questions
2. **Topological ordering** - solve sub-questions in dependency order
3. **Rule injection** - prepend first-order logic rules to prompts
4. **Formal language integration** - translate to theorem provers (e.g., Lean)

**Key innovation:** Treats LLM as dynamic knowledge generator, SKG as constraint system.

**Applications demonstrated:**
- Medical diagnostics
- Climate projections
- Multi-hop QA (68.3% vs 43.2% baseline on some benchmarks)

**LAG Frameworks:**
- **LogicRAG** (Chen et al.): Dynamic DAG construction, rolling memory compression
- **RuAG** (Zhang et al.): MCTS-based rule extraction, natural language rule prompting
- **LAG Cartesian** (Xiao et al.): Cognitive load thresholding, confidence-based termination

### 2.6 RAPTOR

**How it works:**
- Recursive embedding, clustering, and summarization
- Builds hierarchical tree: leaves (chunks) → intermediate (summaries) → root (abstract)
- Uses Gaussian Mixture Model for cluster detection
- Retrieves from multiple tree levels during inference

**Key innovation:** Multi-level abstraction enables reasoning across entire documents.

**Cost efficiency:** Similar to vanilla RAG (no graph traversal overhead).

### 2.7 MMGraphRAG (Multimodal)

**Paper:** https://arxiv.org/abs/2507.20804

**How it works:**
- **Text2KG Module**: Transform text to knowledge graph
- **Image2Graph Module**: Process images to scene graphs
- **Cross-Modal Knowledge Fusion**: Spectral clustering for entity linking
- Retrieves context along reasoning paths across modalities

**Key innovation:** Unified multimodal knowledge graph (MMKG) bridges vision and language.

**Performance:** SOTA on DocBench and MMLongBench datasets.

### 2.8 mKG-RAG

**Paper:** https://arxiv.org/abs/2508.05318

**Focus:** Knowledge-based Visual Question Answering (VQA)

**How it works:**
- Integrates multimodal knowledge graphs into RAG
- Uses Llama-3.2-11B-Vision for multimodal KG construction
- Textual entity-relationship recognition + vision-text matching

---

## 3. Architecture Diagrams

```
VANILLA RAG                          GRAPHRAG (Microsoft)
┌─────────┐                          ┌─────────┐
│ Chunks  │──vector──►LLM            │ Chunks  │──extract──►┌──────────┐
└─────────┘                          └─────────┘            │ Entities │
                                                            │ Relations│
                                                            └────┬─────┘
                                                                 │
                                            community detection──┘
                                                                 │
                                                            ┌────▼─────┐
                                                            │Summaries │
                                                            └────┬─────┘
                                                                 │
                                            global + local query─┘

LIGHTRAG                              HIPPORAG
┌─────────┐                          ┌─────────┐
│ Chunks  │──►┌────────────┐         │ Chunks  │──►┌────────────┐
└─────────┘   │ Entity KG  │         └─────────┘   │ OpenIE KG  │
              └─────┬──────┘                       └─────┬──────┘
                    │                                    │
       dual-level retrieval                    Personalized PageRank
       (low + high level)                      (hippocampal indexing)
                    │                                    │
              ┌─────▼──────┐                       ┌─────▼──────┐
              │ Fast query │                       │ Associative│
              │ (no rebuild)│                      │ retrieval  │
              └────────────┘                       └────────────┘

KAG (Knowledge Augmented)             LAG (Logic Augmented)
┌─────────┐    ┌─────────┐           ┌─────────┐    ┌─────────┐
│ Chunks  │◄──►│ SKG     │           │ LLM as  │◄──►│ SKG     │
└─────────┘    └─────────┘           │ RCKG    │    │ Axioms  │
      │              │               └─────────┘    └─────────┘
      └──────┬───────┘                     │              │
             │                             └──────┬───────┘
      mutual indexing                             │
             │                        dependency decomposition
      ┌──────▼───────┐                            │
      │ Logical form │                     ┌──────▼───────┐
      │ reasoning    │                     │ Sub-question │
      └──────────────┘                     │ DAG solving  │
                                           └──────────────┘

RAPTOR                                MMGRAPHRAG (Multimodal)
┌─────────┐                          ┌─────────┐    ┌─────────┐
│ Chunks  │──cluster──►              │  Text   │    │  Image  │
└─────────┘           │              └────┬────┘    └────┬────┘
                      │                   │              │
            ┌─────────▼─────────┐    Text2KG        Image2Graph
            │ Level 1 summaries │         │              │
            └─────────┬─────────┘         └──────┬───────┘
                      │                          │
            ┌─────────▼─────────┐    cross-modal entity linking
            │ Level 2 summaries │                │
            └─────────┬─────────┘         ┌──────▼───────┐
                      │                   │ Unified MMKG │
            ┌─────────▼─────────┐         └──────────────┘
            │ Root (abstract)   │
            └───────────────────┘
```

---

## 4. Benchmark Performance

### Multi-hop Question Answering

| Framework | HotpotQA F1 | 2WikiMultiHop F1 | Cost (tokens) | Latency |
|-----------|-------------|------------------|---------------|---------|
| Vanilla RAG | ~45% | ~38% | 1x | 1x |
| GraphRAG | ~58% | ~52% | 10-50x | 5-10x |
| LightRAG | ~62% | ~55% | 2-3x | 1.5x |
| HippoRAG | ~65% | ~58% | 1.5x | 1.2x |
| KAG | ~68% | +19.6% relative | 3-5x | 2x |
| LAG | ~68% | ~60% | 3-5x | 2-3x |

### Key Observations

- Graph-based methods consistently outperform vanilla RAG by 5-20 points
- HippoRAG and LightRAG offer best cost/performance tradeoff
- KAG excels in professional domain applications
- GraphRAG best for narrative synthesis but expensive

---

## 5. Integration Ecosystem

| Framework | LangChain | LlamaIndex | Neo4j | Qdrant | Ollama | Python |
|-----------|-----------|------------|-------|--------|--------|--------|
| GraphRAG | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| LightRAG | ✓ | - | - | ✓ | ✓ | ✓ |
| HippoRAG | ✓ | - | ✓ | ✓ | ✓ | ✓ |
| KAG | Custom | - | OpenSPG | - | ✓ | ✓ |
| RAPTOR | ✓ | ✓ | - | ✓ | ✓ | ✓ |

---

## 6. Decision Matrix

### When to Use Each Framework

| If you need... | Use | Why |
|----------------|-----|-----|
| Simple document Q&A | Vanilla RAG | Cheapest, fastest |
| Complex narrative synthesis | GraphRAG | Community summaries excel at "big picture" |
| Fast graph reasoning | LightRAG | No rebuild, dual-level retrieval |
| Human-like memory | HippoRAG | Associative retrieval via PageRank |
| Professional domain expertise | KAG | Mutual indexing + logical reasoning |
| Tacit/implicit knowledge | LAG | LLM as continuous KG + decomposition |
| Long document abstraction | RAPTOR | Hierarchical summaries |
| Images + Text together | MMGraphRAG | Cross-modal entity linking |

---

## 7. Application to Inorganic Chemistry Project

### Current State

| Component | Our Implementation | Status |
|-----------|-------------------|--------|
| Vector DB | Qdrant with 8,756 chunks | ✓ Complete |
| Knowledge Graph | 5,380 nodes, 2,885 edges | ✓ Complete |
| Topic hierarchy | Topic → Subtopic → Concept | ✓ Complete |
| Prerequisite chains | prerequisites, leads_to edges | ✓ Complete |
| Textbook analysis | 7 books × 9 dimensions | ✓ Complete |
| Chunk ↔ Node linking | Not implemented | ✗ Gap |
| Logical reasoning layer | Not implemented | ✗ Gap |

### Framework Applicability

| Our Current State | Framework That Helps | Enhancement |
|-------------------|---------------------|-------------|
| Qdrant chunks (8,756) | **All** | Already have vector base |
| Knowledge graph (5,380 nodes) | **KAG, LightRAG** | Already have graph structure |
| Prerequisites/leads_to edges | **HippoRAG, LAG** | Can do PageRank + decomposition |
| Multi-textbook sources | **GraphRAG** | Community detection across books |
| No chunk↔node linking | **KAG** | Need mutual indexing |
| No visual content yet | **MMGraphRAG** | Future: diagrams, structures |

### Recommended Hybrid Approach: ChemKG-RAG

```
┌─────────────────────────────────────────────────────────────────┐
│              PROPOSED: ChemKG-RAG (Hybrid Framework)             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   FROM KAG:           FROM LAG:           FROM HIPPORAG:        │
│   • Mutual indexing   • Sub-question      • PageRank on         │
│   • Chunk ↔ Node        decomposition       prerequisites       │
│     bidirectional     • Dependency DAG    • Associative         │
│                                             retrieval           │
│                                                                  │
│   FROM LIGHTRAG:      FROM GRAPHRAG:      FROM RAPTOR:          │
│   • Dual-level        • Cross-textbook    • Hierarchical        │
│     (concept +          community           topic summaries     │
│      topic level)       detection                               │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                    IMPLEMENTATION PRIORITY                       │
│                                                                  │
│   1. Mutual Indexing (KAG)      ─── Foundation for everything   │
│   2. PageRank on prereqs        ─── "What to learn first?"      │
│   3. Sub-question decomposition ─── Complex chemistry queries   │
│   4. Cross-book communities     ─── Synthesize perspectives     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation Pseudo-code

```python
# ChemKG-RAG: Hybrid approach combining best of each framework

def answer_complex_question(question: str, knowledge_graph: dict) -> str:
    # 1. LAG: decompose question into sub-questions
    sub_questions = decompose(question)

    # 2. LAG: build dependency DAG
    dag = build_dependency_dag(sub_questions)

    # 3. for each sub-question in topological order:
    answers = {}
    for sq in topological_sort(dag):
        # KAG: get relevant topics from our KG
        topics = find_relevant_topics(sq, knowledge_graph)

        # HippoRAG: PageRank on prerequisite graph
        prereqs = pagerank_prerequisites(topics, knowledge_graph)

        # KAG: retrieve source chunks via mutual indexing
        chunks = get_chunks_for_topics(topics)

        # LightRAG: dual-level retrieval (concept + topic)
        context = dual_level_retrieve(sq, chunks, topics)

        # generate answer with full context
        answers[sq] = llm_generate(sq, context, prereqs, answers)

    # 4. synthesize final answer
    return synthesize(question, answers)
```

---

## 8. References

### Primary Sources

1. **GraphRAG**: https://github.com/microsoft/graphrag
2. **LightRAG**: https://github.com/HKUDS/LightRAG
3. **HippoRAG**: https://github.com/OSU-NLP-Group/HippoRAG
4. **KAG**: https://github.com/OpenSPG/KAG
5. **LAG**: https://arxiv.org/abs/2411.14012
6. **MMGraphRAG**: https://arxiv.org/abs/2507.20804
7. **mKG-RAG**: https://arxiv.org/abs/2508.05318

### Integration Resources

8. **Neo4j GraphRAG**: https://neo4j.com/blog/genai/what-is-graphrag/
9. **LangChain KG Integration**: https://www.blog.langchain.com/enhancing-rag-based-applications-accuracy-by-constructing-and-leveraging-knowledge-graphs/
10. **LlamaIndex Neo4j**: https://neo4j.com/labs/genai-ecosystem/llamaindex/

### Surveys & Comparisons

11. **RAG 2024 Year in Review**: https://ragflow.io/blog/the-rise-and-evolution-of-rag-in-2024-a-year-in-review
12. **Awesome-GraphRAG**: https://github.com/DEEP-PolyU/Awesome-GraphRAG
13. **Multimodal RAG Survey**: https://github.com/llm-lab-org/Multimodal-RAG-Survey

---

## 9. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-18 | Initial comprehensive survey |

---

*Document maintained by: Claude Code + Kiran Boggavarapu*
*Review frequency: As new frameworks emerge*
