# Novel Pedagogy: Graph-Based Learning

**The problem:** Traditional curricula are linear. Students don't see connections.

**Our asset:** 1,458 prerequisite edges + 5,380 concepts + 4 scales.

---

## 3 Novel Features

### 1. BRIDGE EXPLANATIONS

When teaching a concept, explicitly show HOW it connects to what student already knows.

**Traditional:**
> "Session 21: Crystal Field Theory. In octahedral complexes, d-orbitals split into t2g and eg sets..."

**Novel:**
> "You learned d-orbitals have different shapes (Session 1). You learned ligands have lone pairs (Session 17). Now: What happens when 6 ligands approach a metal? The ligands' electrons REPEL the metal's d-electrons. Orbitals pointing AT ligands (eg) go UP in energy. Orbitals pointing BETWEEN ligands (t2g) stay lower."

**Implementation:** For each topic, query the graph for prerequisite edges. Generate bridge sentence:
```
"You learned [PREREQUISITE] in [SESSION]. Now see how it explains [CURRENT TOPIC]..."
```

---

### 2. SCALE ZOOM

Every phenomenon exists at all 4 scales. Let student zoom in/out.

**Example: "Why is copper sulfate blue?"**

| Scale | Explanation | Depth |
|-------|-------------|-------|
| **DESCRIPTIVE** | Copper compounds are often blue or green | What happens |
| **STRUCTURAL** | Cu²⁺ is d⁹ in octahedral [Cu(H₂O)₆]²⁺ | How it's arranged |
| **ELECTRONIC** | d-d transition absorbs orange (~600nm), transmits blue | Why it happens |
| **QUANTUM** | Selection rules (Laporte forbidden, spin allowed) explain weak absorption | Fundamental basis |

**Implementation:** Tag every concept with scale. Provide zoom buttons:
```
[DESCRIPTIVE] ←→ [STRUCTURAL] ←→ [ELECTRONIC] ←→ [QUANTUM]
     ↑                                              ↑
  "What"                                        "Why (deep)"
```

---

### 3. QUESTION-DRIVEN PATHS

Student asks a question. System traces prerequisites and builds personalized path.

**Student asks:** "How do MRI contrast agents work?"

**System traces:**
```
MRI contrast agents
    ↓ requires
Magnetic moment of metal ions
    ↓ requires
Unpaired electrons
    ↓ requires
Crystal field theory / d-electron config
    ↓ requires
d-orbital splitting
    ↓ requires
Atomic orbital shapes
```

**System generates path:**
1. Quick review: Atomic orbitals (5 min)
2. Quick review: d-orbital splitting in octahedral (10 min)
3. New: High-spin vs low-spin (15 min)
4. New: Magnetic moment calculation (10 min)
5. Application: MRI contrast agents (20 min)

**Implementation:** Reverse-traverse prerequisite edges from target concept. Check what student already knows. Build minimal path.

---

## Comparison

| Aspect | Traditional | Novel |
|--------|-------------|-------|
| Structure | Linear (Ch 1→2→3) | Graph (interconnected) |
| Connections | Implicit | Explicit bridges |
| Starting point | Chapter 1 | Any question |
| Depth | Fixed | Zoomable (4 scales) |
| Prerequisites | Assumed | Traced & reviewed |
| Student agency | Follow syllabus | Choose entry point |

---

## Data We Already Have

| Asset | Use |
|-------|-----|
| 1,458 prerequisite edges | Build paths, generate bridges |
| 5,380 concepts | Fine-grained learning units |
| 4 scales (Q/E/S/D) | Zoom functionality |
| 7 textbooks | Source-specific explanations |
| PageRank scores | Identify foundational concepts |

---

## Minimum Viable Implementation

### Phase 1: Bridge Generator
```python
def generate_bridge(concept, student_history):
    """Generate explicit connection to prior knowledge."""
    prereqs = graph.get_prerequisites(concept)
    known = [p for p in prereqs if p in student_history]

    if known:
        return f"You learned {known[0]} earlier. Now see how {concept} builds on it..."
    else:
        return f"Before {concept}, you need: {prereqs[:3]}..."
```

### Phase 2: Scale Zoom UI
```html
<div class="scale-selector">
  <button data-scale="descriptive">What happens</button>
  <button data-scale="structural">How arranged</button>
  <button data-scale="electronic">Why happens</button>
  <button data-scale="quantum">Deep why</button>
</div>
<div id="explanation">
  <!-- Changes based on selected scale -->
</div>
```

### Phase 3: Question-Driven Path
```python
def build_path(target_concept, student_knows):
    """Build minimal path from known concepts to target."""
    path = []
    to_learn = get_all_prerequisites(target_concept)
    to_learn = [t for t in to_learn if t not in student_knows]

    # Topological sort
    return topological_sort(to_learn) + [target_concept]
```

---

## Why This Works Pedagogically

1. **Reduces cognitive load** - Student sees WHY they're learning something
2. **Builds on prior knowledge** - Explicit connections to what they know
3. **Supports different learners** - Start from interest, not chapter 1
4. **Enables depth control** - Zoom to appropriate level
5. **Makes prerequisites visible** - No hidden assumptions

---

## Next Step

Build a prototype with ONE topic (e.g., CFT) showing:
1. Prerequisites traced
2. Bridges generated
3. Scale zoom working
4. Question "Why is CuSO4 blue?" answered at all 4 scales
