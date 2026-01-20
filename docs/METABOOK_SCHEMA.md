# Meta-Book Schema: Data-Driven Lesson Generation

**Purpose:** Define the structure for synthesizing lessons from knowledge graph + textbooks
**Status:** DRAFT - Needs review
**Date:** 2026-01-19

---

## Overview

The Meta-Book is a **machine-readable curriculum** that combines:
1. Knowledge graph (prerequisites, relationships, scales)
2. Textbook analysis (10 books, coverage ratings, examples)
3. Hierarchical model (4 scales, trees within scales)
4. Learning objectives (SLOs, Bloom's levels)

```
┌─────────────────────────────────────────────────────────────────┐
│                     META-BOOK ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐          │
│   │  Knowledge  │   │  Textbook   │   │Hierarchical │          │
│   │    Graph    │   │  Analysis   │   │   Model     │          │
│   │ (5380 nodes)│   │ (10 books)  │   │ (4 scales)  │          │
│   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘          │
│          │                 │                 │                   │
│          └────────────┬────┴────────────────┘                   │
│                       ▼                                          │
│              ┌─────────────────┐                                │
│              │   META-BOOK     │                                │
│              │  (JSON Schema)  │                                │
│              └────────┬────────┘                                │
│                       │                                          │
│          ┌────────────┼────────────┐                            │
│          ▼            ▼            ▼                            │
│   ┌───────────┐ ┌───────────┐ ┌───────────┐                    │
│   │  Lessons  │ │Assessments│ │  Learning │                    │
│   │           │ │           │ │   Paths   │                    │
│   └───────────┘ └───────────┘ └───────────┘                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Schema Definition

### Top-Level Structure

```json
{
  "meta": {
    "version": "1.0.0",
    "course": "CHEM 361",
    "title": "Inorganic Chemistry Meta-Book",
    "generated": "2026-01-19",
    "sources": {
      "knowledge_graph": "chemkg_enhanced.json",
      "textbooks": ["list of 10 books"],
      "model": "hierarchical_4_scale"
    }
  },
  "units": [...],           // 3 course units
  "lessons": [...],         // 23 individual lessons
  "topics": {...},          // Topic metadata dictionary
  "assessments": {...},     // Quiz/exam question bank
  "learning_paths": {...}   // Personalized progression
}
```

### Unit Schema

```json
{
  "id": "unit_1",
  "name": "Main Group Chemistry",
  "scale": "DESCRIPTIVE",
  "sessions": 9,
  "weeks": "1-5",
  "slos": ["SLO1", "SLO5"],
  "lessons": ["lesson_1", "lesson_2", ...],
  "hub_topics": ["Periodic Trends", "Redox Chemistry"],
  "assessment": {
    "midterm": true,
    "quizzes": [1, 2, 3, 4]
  }
}
```

### Lesson Schema

```json
{
  "id": "lesson_5",
  "title": "Crystal Field Theory: Octahedral Complexes",
  "unit": "unit_2",
  "session": 5,
  "duration_minutes": 75,

  "scale": {
    "primary": "ELECTRONIC",
    "touches": ["STRUCTURAL"],
    "escalation_from": "Coordination Geometry"
  },

  "topic": {
    "name": "Crystal Field Theory",
    "pagerank": 0.0017,
    "mentions": 165,
    "hub_score": 0.85
  },

  "prerequisites": {
    "required": ["Coordination Geometry", "Atomic Orbitals"],
    "recommended": ["Symmetry Basics"],
    "scale_prerequisites": {
      "STRUCTURAL": ["Octahedral geometry"],
      "QUANTUM": ["d-orbital shapes"]
    }
  },

  "learning_objectives": [
    {
      "id": "LO_5_1",
      "text": "Draw the d-orbital splitting diagram for octahedral complexes",
      "bloom_level": "apply",
      "scale": "ELECTRONIC",
      "assessment_type": "diagram"
    },
    {
      "id": "LO_5_2",
      "text": "Calculate CFSE for high-spin and low-spin configurations",
      "bloom_level": "apply",
      "scale": "ELECTRONIC",
      "assessment_type": "calculation"
    }
  ],

  "content_synthesis": {
    "best_explanation": {
      "source": "Atkins_Shriver",
      "rating": 5,
      "pages": "456-462",
      "approach": "orbital_diagram_first"
    },
    "best_examples": {
      "source": "JD_Lee",
      "rating": 4,
      "examples": ["[Fe(H2O)6]²⁺", "[Co(NH3)6]³⁺"]
    },
    "best_visuals": {
      "source": "descriptive_ic",
      "rating": 5,
      "figures": ["d-orbital_splitting.png"]
    },
    "cross_references": [
      {"book": "House", "pages": "312-318", "strength": "worked_problems"},
      {"book": "Tina", "pages": "201-210", "strength": "applications"}
    ]
  },

  "subtopics": [
    {
      "name": "d-orbital splitting",
      "time_allocation": 20,
      "key_points": ["t2g and eg sets", "Δo parameter"],
      "common_misconceptions": ["Splitting magnitude vs geometry"]
    },
    {
      "name": "Spectrochemical series",
      "time_allocation": 15,
      "key_points": ["Ligand ordering", "Field strength"],
      "common_misconceptions": ["Charge vs field strength"]
    }
  ],

  "worked_examples": [
    {
      "problem": "Predict the number of unpaired electrons in [Fe(CN)6]⁴⁻",
      "type": "calculation",
      "difficulty": "medium",
      "solution_steps": ["Identify Fe oxidation state", "Count d electrons", "Apply strong field"],
      "source": "adapted from Atkins"
    }
  ],

  "assessment_items": {
    "formative": [
      {"type": "clicker", "question": "Which has larger Δo: [Fe(H2O)6]²⁺ or [Fe(CN)6]⁴⁻?"},
      {"type": "think_pair_share", "prompt": "Why is [Co(NH3)6]³⁺ yellow?"}
    ],
    "summative": {
      "quiz_questions": ["quiz_5_q1", "quiz_5_q2"],
      "exam_questions": ["exam1_q3"]
    }
  },

  "connections": {
    "forward": ["Color and Magnetism", "Jahn-Teller Distortion"],
    "backward": ["Coordination Geometry", "Atomic Orbitals"],
    "lateral": ["MO Theory comparison"],
    "applications": ["Gemstone colors", "MRI contrast agents"]
  }
}
```

### Topic Metadata Schema

```json
{
  "Crystal Field Theory": {
    "id": "topic_cft",
    "scale": "ELECTRONIC",
    "tree": "bonding_theories",

    "graph_metrics": {
      "pagerank": 0.0017,
      "in_degree": 12,
      "out_degree": 8,
      "hub_score": 0.85,
      "betweenness": 0.023
    },

    "textbook_coverage": {
      "Atkins_Shriver": {"rating": 5, "chunks": 144},
      "JD_Lee": {"rating": 4, "chunks": 89},
      "House": {"rating": 4, "chunks": 76}
    },

    "subtopics": [
      "d-orbital splitting",
      "Spectrochemical series",
      "CFSE",
      "High-spin/low-spin",
      "Jahn-Teller"
    ],

    "prerequisites": ["Coordination Geometry", "Atomic Orbitals"],
    "leads_to": ["Color prediction", "Magnetism", "Thermodynamics"],

    "scale_context": {
      "why_this_scale": "Explains electronic structure effects on properties",
      "escalation_trigger": "Why do d-orbitals split?",
      "escalation_target": "QUANTUM (ligand field theory)"
    }
  }
}
```

### Assessment Item Schema

```json
{
  "quiz_5_q1": {
    "id": "quiz_5_q1",
    "topic": "Crystal Field Theory",
    "scale": "ELECTRONIC",
    "bloom_level": "apply",

    "question": {
      "stem": "For [Mn(H2O)6]²⁺, predict whether the complex is high-spin or low-spin.",
      "type": "short_answer",
      "points": 5
    },

    "rubric": {
      "full_credit": "Identifies weak field ligand → high spin with 5 unpaired electrons",
      "partial_credit": "Correct reasoning, wrong count",
      "common_errors": ["Confusing Mn²⁺ with Mn⁴⁺", "Forgetting water is weak field"]
    },

    "alignment": {
      "lesson": "lesson_5",
      "learning_objective": "LO_5_2",
      "slo": "SLO2"
    },

    "difficulty": {
      "estimated": 0.65,
      "actual": null,
      "discrimination": null
    }
  }
}
```

### Learning Path Schema

```json
{
  "standard_path": {
    "name": "Default Curriculum Order",
    "description": "Data-driven sequence: Main Group → Coordination → Solid State",
    "lessons": ["lesson_1", "lesson_2", ..., "lesson_23"]
  },

  "remediation_paths": {
    "weak_periodic_trends": {
      "trigger": "pretest_score < 60%",
      "insert_before": "lesson_1",
      "supplemental": ["review_periodic_table", "practice_trends"]
    },
    "weak_orbitals": {
      "trigger": "quiz_3_score < 70%",
      "insert_before": "lesson_5",
      "supplemental": ["review_orbitals", "practice_electron_config"]
    }
  },

  "acceleration_paths": {
    "strong_foundation": {
      "trigger": "pretest_score > 90%",
      "skip": ["lesson_1"],
      "start_at": "lesson_2"
    }
  },

  "hub_checkpoints": {
    "periodic_trends": {
      "after_lesson": "lesson_3",
      "assessment": "hub_check_1",
      "threshold": 0.75,
      "remediation": "remediation_paths.weak_periodic_trends"
    }
  }
}
```

---

## Scale-Aware Content Tagging

Every content element tagged with:

| Tag | Values | Purpose |
|-----|--------|---------|
| `scale` | QUANTUM, ELECTRONIC, STRUCTURAL, DESCRIPTIVE | Primary abstraction level |
| `tree` | e.g., "main_group", "cft", "crystal_structures" | Tree within scale |
| `depth` | 0-3 | Position within tree (0=root) |
| `escalation` | boolean | Does this require going to deeper scale? |

### Example Tagging

```json
{
  "content_block": "The color of [Cu(H2O)6]²⁺ arises from d-d transitions...",
  "tags": {
    "scale": "ELECTRONIC",
    "tree": "crystal_field_theory",
    "depth": 1,
    "escalation": false,
    "touches_scales": ["STRUCTURAL"]
  }
}
```

---

## Data Sources Mapping

| Schema Field | Source |
|--------------|--------|
| `topic.pagerank` | `chemkg_enhanced.json` |
| `topic.mentions` | `chemkg_enhanced.json` |
| `content_synthesis.best_*` | `textbook_analysis_v2.json` |
| `prerequisites` | `chemkg_enhanced.json` edges |
| `scale` | `HIERARCHICAL_KNOWLEDGE_MODEL.md` rules |
| `hub_score` | `dual_pagerank_curriculum.py` |
| `learning_objectives` | Manual + SLO alignment |

---

## Generation Process

```
1. EXTRACT topic list from knowledge graph
   ↓
2. ASSIGN scale and tree membership
   ↓
3. ORDER by hybrid curriculum algorithm
   ↓
4. MAP to 23 sessions (time allocation by coverage)
   ↓
5. SYNTHESIZE content from best textbook sources
   ↓
6. ALIGN learning objectives with Bloom's + SLOs
   ↓
7. GENERATE assessment items at appropriate scales
   ↓
8. BUILD learning paths with hub checkpoints
   ↓
9. EXPORT as meta-book JSON
```

---

## File Structure

```
meta-book/
├── metabook.json              # Full compiled meta-book
├── units/
│   ├── unit_1_main_group.json
│   ├── unit_2_coordination.json
│   └── unit_3_solid_state.json
├── lessons/
│   ├── lesson_01.json
│   ├── lesson_02.json
│   └── ... (23 total)
├── topics/
│   └── topic_metadata.json    # All topic data
├── assessments/
│   ├── quizzes.json
│   ├── exams.json
│   └── formative.json
└── paths/
    └── learning_paths.json
```

---

## Open Questions for Discussion

1. **Granularity:** Is 23 lessons the right level? Should we have sub-lessons?

2. **Content depth:** How much actual content (explanations, examples) vs. pointers to textbooks?

3. **Assessment density:** How many questions per topic/lesson?

4. **Personalization:** How sophisticated should learning paths be?

5. **Export formats:** JSON primary, but also Markdown for humans? HTML for LMS?

6. **Versioning:** How to track changes as we refine?

---

## Next Steps

1. [ ] Review and finalize schema with user
2. [ ] Build generator script from existing data
3. [ ] Generate first draft meta-book
4. [ ] Validate against existing schedule.json
5. [ ] Create sample lesson in full detail

---

*Part of the Knowledge Graph Pedagogy Project*
*McNeese State University, CHEM 361*
