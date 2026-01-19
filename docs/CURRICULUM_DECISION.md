# Curriculum Decision: Data-Driven Reordering

**Decision Date:** 2026-01-18
**Decision:** Adopt data-driven curriculum order
**Status:** APPROVED

---

## The Decision

```
OLD ORDER:  Coordination → Main Group → Solid State
NEW ORDER:  Main Group → Coordination → Solid State
```

**Rationale:** "We go by data, that is the point."

---

## Evidence Supporting This Decision

### From Knowledge Graph Analysis

| Metric | Main Group | Coordination | Solid State |
|--------|------------|--------------|-------------|
| PageRank | **0.0432** (highest) | 0.0132 | 0.0069 |
| Coverage | **40%** | 43% | 17% |
| Prerequisite Role | Foundation for CFT | Needs periodic trends | Needs both |

### The Prerequisite Chain

```
Periodic Trends (Main Group)
    ↓ required for
Electron Configuration
    ↓ required for
Crystal Field Theory (Coordination)
    ↓ required for
Color/Magnetism predictions
```

Teaching CFT **before** periodic trends forces students to accept concepts without understanding the foundation.

---

## New Curriculum Structure

### Unit 1: Main Group Chemistry (9 teaching sessions)
**Scale:** Primarily DESCRIPTIVE
**Purpose:** Build foundational understanding of elements, trends, properties

| Week | Topics | Scale |
|------|--------|-------|
| 1 | Periodic trends (atomic properties, ionization, EN) | DESCRIPTIVE |
| 2 | Hydrogen, hydrides, Groups 1 & 2 | DESCRIPTIVE |
| 3 | Groups 13-16 | DESCRIPTIVE |
| 4 | Groups 17-18, periodic review | DESCRIPTIVE |
| 5 | Redox chemistry → **EXAM 1** | DESCRIPTIVE |

### Unit 2: Coordination Chemistry (8 teaching sessions)
**Scale:** STRUCTURAL → ELECTRONIC
**Purpose:** Apply periodic trends to transition metal complexes

| Week | Topics | Scale |
|------|--------|-------|
| 6 | Introduction, ligands, coordination number | STRUCTURAL |
| 7 | Nomenclature (Mardi Gras break) | STRUCTURAL |
| 8 | Isomerism, CFT intro | STRUCTURAL → ELECTRONIC |
| 9 | CFT geometries, CFSE | ELECTRONIC |
| 10 | Color, magnetism → **EXAM 2** | ELECTRONIC |

### Unit 3: Solid State Chemistry (5 teaching sessions)
**Scale:** STRUCTURAL + ELECTRONIC
**Purpose:** Extend concepts to extended structures

| Week | Topics | Scale |
|------|--------|-------|
| 11 | Unit cells, ionic structures | STRUCTURAL |
| 12 | Band theory, applications | ELECTRONIC |
| 13 | Course synthesis, review | all |
| 14-15 | Presentations, **FINAL EXAM** | — |

---

## Session Allocation

| Unit | Old | New | Change | Justification |
|------|-----|-----|--------|---------------|
| Main Group | 7 | 9 | +2 | 40% coverage, foundational |
| Coordination | 9 | 8 | -1 | Still substantial, but after foundation |
| Solid State | 7 | 5 | -2 | 17% coverage, builds on both |

Total teaching sessions: 22 (unchanged)

---

## Scale Tagging

Each lecture is now tagged with its primary scale level:

```
DESCRIPTIVE  → What happens (properties, trends, reactions)
STRUCTURAL   → How it's arranged (geometry, isomers, nomenclature)
ELECTRONIC   → Why it happens (CFT, MO, bonding)
QUANTUM      → Fundamental why (rarely needed at 300-level)
```

**Navigation rule:** Stay at DESCRIPTIVE/STRUCTURAL when possible. Escalate to ELECTRONIC only for "why" questions about color, magnetism, reactivity.

---

## Student Learning Progress Tracking

### What to Track

1. **Pre-test:** Periodic trends knowledge (Gen Chem carry-over)
2. **Quiz performance by scale:** Do students struggle more with ELECTRONIC than DESCRIPTIVE?
3. **Misconception patterns:** Where do prerequisite gaps show up?
4. **Cross-unit transfer:** Can students apply Main Group concepts to Coordination?

### Data Collection Points

| Week | Assessment | Data Collected |
|------|------------|----------------|
| 1 | Pre-test | Baseline periodic trends knowledge |
| 1-4 | Quizzes 1-4 | Main Group concept mastery |
| 5 | Exam 1 | Unit 1 comprehensive |
| 6-10 | Quizzes 5-8 | Coordination concept mastery |
| 10 | Exam 2 | Unit 2 + transfer from Unit 1 |
| 11-12 | Quizzes 9-10 | Solid State concept mastery |
| 15 | Final | Comprehensive + integration |

### Metrics to Compute

1. **Scale difficulty:** Avg score on DESCRIPTIVE vs STRUCTURAL vs ELECTRONIC questions
2. **Prerequisite effectiveness:** Correlation between Unit 1 and Unit 2 scores
3. **Transfer success:** Performance on questions requiring cross-unit concepts
4. **Concept retention:** Final exam vs earlier assessments

---

## Comparison Study Design

### Research Question

> Does teaching Main Group before Coordination improve student learning outcomes compared to the traditional order?

### Methodology

**This semester (Spring 2025):** Data-driven order (MG → Coord → SS)
**Comparison:** Historical data from previous semesters (if available) or published norms

### Outcomes to Measure

1. Overall course grades
2. Unit-specific exam scores
3. Concept inventory scores (if using standardized instrument)
4. Student self-reported understanding
5. Performance on "integration" questions

---

## File Locations

| File | Purpose |
|------|---------|
| `data/schedule.json` | Original (Coord first) |
| `data/schedule_data_driven.json` | New (MG first) |
| `experiments/results/curriculum_comparison.json` | Analysis data |

---

## Approval

**Instructor:** Kiran Boggavarapu
**Date:** 2026-01-18
**Basis:** Knowledge graph analysis of 7 textbooks (5,380 nodes)

---

*"We go by data, that is the point."*
