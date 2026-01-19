# Hierarchical Knowledge Model: Scale-Aware Curriculum Design

**Purpose:** A new framework for organizing chemistry knowledge that respects natural abstraction boundaries
**Insight Origin:** Session 4 discussion on curriculum generation
**Date:** 2026-01-18

---

## The Core Insight

### The Problem with Flat Graphs

Traditional prerequisite graphs treat knowledge as a 2D network:
```
Topic A → Topic B → Topic C → Topic D
```

This creates a "blind path" problem: if you trace back far enough, **everything leads to electrons**. But this doesn't help pedagogy because:

- You don't need quantum mechanics to learn nomenclature
- Understanding building architecture doesn't require knowing atomic physics
- Each scale of understanding is **self-contained** for certain purposes

### The Bricks Analogy

> "Although a building has bricks and bricks have atoms and atoms have electrons, this does not help. After bricks we have different hierarchy. Understanding building should stop at bricks, understanding bricks should stop at meso, and understanding meso to nano to atoms. A blind path by definition leads to electrons."

This insight reveals that knowledge exists at **multiple scales**, and each scale has its own complete understanding that doesn't require drilling down further.

---

## The Four Scales of Inorganic Chemistry

```
╔═════════════════════════════════════════════════════════════════════╗
║                    HIERARCHICAL KNOWLEDGE SCALES                     ║
╠═════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  SCALE 4: QUANTUM (Nano)                                            ║
║  ══════════════════════                                             ║
║  "The fundamental why"                                              ║
║  • Wave functions, quantum numbers                                  ║
║  • Spin-orbit coupling, relativistic effects                        ║
║  • Electron configuration from first principles                     ║
║  • When needed: Explaining anomalies, heavy elements, fine details  ║
║                                                                      ║
║         ▲                                                           ║
║         │ Escalate only when electronic explanation insufficient    ║
║         │                                                           ║
║  SCALE 3: ELECTRONIC (Micro)                                        ║
║  ═══════════════════════════                                        ║
║  "Why it happens"                                                   ║
║  • Crystal Field Theory, Ligand Field Theory                        ║
║  • Molecular Orbital diagrams                                       ║
║  • Bonding theories (VB, MO, CFT)                                   ║
║  • When needed: Explaining color, magnetism, reactivity             ║
║                                                                      ║
║         ▲                                                           ║
║         │ Escalate only when structural explanation insufficient    ║
║         │                                                           ║
║  SCALE 2: STRUCTURAL (Meso)                                         ║
║  ══════════════════════════                                         ║
║  "How it's arranged"                                                ║
║  • Coordination geometry, crystal structures                        ║
║  • Isomerism, symmetry, point groups                                ║
║  • Nomenclature, formulas                                           ║
║  • When needed: Describing compounds, predicting shapes             ║
║                                                                      ║
║         ▲                                                           ║
║         │ Escalate only when descriptive facts insufficient         ║
║         │                                                           ║
║  SCALE 1: DESCRIPTIVE (Macro)                                       ║
║  ═════════════════════════════                                      ║
║  "What happens"                                                     ║
║  • Periodic trends, group properties                                ║
║  • Reactions, products, observations                                ║
║  • Element-specific chemistry                                       ║
║  • When needed: Factual knowledge, pattern recognition              ║
║                                                                      ║
╚═════════════════════════════════════════════════════════════════════╝
```

---

## Trees Within Each Scale

Each scale is not a flat list but contains **multiple trees** of related concepts:

### Scale 1: DESCRIPTIVE Trees

```
Main Group Chemistry                    Transition Metal Chemistry
├── Alkali Metals (Group 1)            ├── First Row (Sc-Zn)
│   ├── Reactivity with water          │   ├── Common oxidation states
│   ├── Flame colors                   │   ├── Color trends
│   └── Compounds                      │   └── Catalytic properties
├── Alkaline Earth (Group 2)           ├── Second Row (Y-Cd)
├── Halogens (Group 17)                └── Third Row (Lanthanide contraction)
└── Noble Gases (Group 18)

Periodic Trends
├── Atomic radius
├── Ionization energy
├── Electronegativity
└── Electron affinity
```

### Scale 2: STRUCTURAL Trees

```
Coordination Chemistry                  Crystal Structures
├── Nomenclature                       ├── Unit cells
│   ├── Ligand naming                  │   ├── Cubic (sc, bcc, fcc)
│   ├── Complex ion naming             │   ├── Hexagonal
│   └── Isomer designation             │   └── Tetragonal
├── Isomerism                          ├── Packing efficiency
│   ├── Geometric (cis/trans)          ├── Coordination number
│   ├── Optical                        └── Radius ratio rules
│   └── Linkage
├── Geometry
│   ├── Octahedral
│   ├── Tetrahedral
│   ├── Square planar
│   └── Others
└── Coordination number

Symmetry
├── Point groups
├── Symmetry operations
├── Character tables
└── Group theory applications
```

### Scale 3: ELECTRONIC Trees

```
Crystal Field Theory                    Molecular Orbital Theory
├── d-orbital splitting                ├── Atomic orbital combinations
│   ├── Octahedral (t2g, eg)          │   ├── σ bonding
│   ├── Tetrahedral                    │   ├── π bonding
│   └── Square planar                  │   └── δ bonding
├── Spectrochemical series             ├── MO diagrams
├── CFSE calculations                  │   ├── Homonuclear diatomics
├── High-spin vs low-spin              │   └── Heteronuclear
├── Jahn-Teller distortion             └── Bond order
└── Magnetism predictions

Chemical Bonding
├── Ionic bonding
│   ├── Lattice energy
│   └── Born-Haber cycle
├── Covalent bonding
│   ├── Lewis structures
│   └── VSEPR
└── Metallic bonding
```

### Scale 4: QUANTUM Trees

```
Atomic Structure                        Quantum Mechanics
├── Electron configuration             ├── Wave functions
│   ├── Aufbau principle               ├── Schrödinger equation
│   ├── Hund's rule                    ├── Quantum numbers (n,l,ml,ms)
│   └── Pauli exclusion                └── Probability distributions
├── Orbital shapes (s,p,d,f)
├── Radial distribution                Relativistic Effects
├── Shielding and penetration          ├── Mass increase
└── Effective nuclear charge           ├── Orbital contraction
                                       └── Color of gold, liquid Hg
```

---

## Navigation Rules

### Rule 1: Stay Within Scale When Possible

Most learning objectives can be satisfied within a single scale:

| Learning Objective | Scale | No need to go deeper |
|-------------------|-------|---------------------|
| Name [Co(NH3)6]Cl3 | STRUCTURAL | Nomenclature tree only |
| List alkali metal reactions | DESCRIPTIVE | Group 1 tree only |
| Draw unit cell of NaCl | STRUCTURAL | Crystal structure tree only |
| State periodic trends | DESCRIPTIVE | Periodic trends tree only |

### Rule 2: Escalate Only When Explanation Required

Cross-scale movement happens when "why" questions arise:

| Question | Starts at | Escalates to | Reason |
|----------|-----------|--------------|--------|
| "Why is [Ti(H2O)6]³⁺ purple?" | STRUCTURAL | ELECTRONIC | Need CFT for color |
| "Why is Fe²⁺ paramagnetic?" | DESCRIPTIVE | ELECTRONIC | Need d-electrons |
| "Why is Au gold-colored?" | DESCRIPTIVE | QUANTUM | Need relativistic effects |
| "What is the geometry?" | STRUCTURAL | (stays) | Geometry is structural |

### Rule 3: Blind Path = Maximum Depth

A "blind path" traces all the way to quantum level. These are rare and only needed for:
- Anomalous properties (lanthanide contraction, relativistic effects)
- Theoretical derivations
- Research-level understanding

```
BLIND PATH EXAMPLE:
  "Why is mercury liquid at room temperature?"

  DESCRIPTIVE: Mercury is liquid (observation)
       ↓ why?
  STRUCTURAL: Weak metallic bonding
       ↓ why weak?
  ELECTRONIC: Filled d and s orbitals, poor overlap
       ↓ why poor overlap?
  QUANTUM: Relativistic contraction of 6s orbital
       ✓ STOP - fundamental explanation reached
```

### Rule 4: Tree Navigation Before Scale Escalation

Before going to a deeper scale, explore siblings and parents within current scale:

```
EXAMPLE: Understanding isomerism

WRONG: isomerism → bonding → orbitals → quantum
       (unnecessary escalation)

RIGHT: isomerism → geometric → cis/trans → optical → linkage
       (explore STRUCTURAL tree fully first)

       Only escalate if asked: "Why do isomers have different properties?"
       Then: STRUCTURAL → ELECTRONIC (for energy/stability differences)
```

---

## Validation from Knowledge Graph Data

Analysis of the ChemKG (5,380 nodes, 7 textbooks) validates this model:

### Topics per Scale

| Scale | Topics (≥10 mentions) | Total Mentions | Avg PageRank |
|-------|----------------------|----------------|--------------|
| DESCRIPTIVE | 6 | 1,714 | 0.0078 |
| STRUCTURAL | 10 | 1,443 | 0.0014 |
| ELECTRONIC | 2 | 294 | 0.0023 |
| QUANTUM | 6 | 186 | 0.0015 |
| APPLICATION | 43 | 2,182 | 0.0006 |

### Cross-Scale Prerequisite Flow

From the prerequisite edge analysis:

```
FROM →        QUANTUM  ELECTRONIC  STRUCTURAL  DESCRIPTIVE  APPLICATION
─────────────────────────────────────────────────────────────────────────
QUANTUM          26         16          11           9           14
ELECTRONIC        7         14          19          11           17
STRUCTURAL       31         24          22          18           40
DESCRIPTIVE       9         14          20          30          100
APPLICATION       9         18          32          29          135
```

**Key observations:**
- Most edges stay within scale or go to APPLICATION (teaching leads to doing)
- QUANTUM → ELECTRONIC (16 edges) confirms the escalation path
- DESCRIPTIVE has most self-references (30) - it's a self-contained foundation

### Self-Contained Topics (Endpoints)

Topics that don't require deeper understanding:

**DESCRIPTIVE endpoints:**
- Redox Chemistry
- Transition Metals
- Actinide Chemistry

**STRUCTURAL endpoints:**
- Symmetry And Group Theory
- Symmetry And Point Groups
- Solid-State Structures

These can be taught without escalating to electronic or quantum levels.

---

## Implications for Curriculum Design

### Current Approach (Flat Graph)

```python
# Old curriculum generator
def topological_sort(topics, prerequisites):
    # Treats all prerequisites equally
    # May jump scales unnecessarily
    return sorted_topics
```

### Proposed Approach (Scale-Aware)

```python
# New curriculum generator concept
def scale_aware_curriculum(topics, scale_tags, trees):
    curriculum = []

    for scale in [DESCRIPTIVE, STRUCTURAL, ELECTRONIC, QUANTUM]:
        # 1. Get topics at this scale
        scale_topics = filter_by_scale(topics, scale)

        # 2. For each tree at this scale
        for tree in get_trees_at_scale(scale):
            # 3. Traverse tree (breadth-first or depth-first)
            tree_order = traverse_tree(tree)
            curriculum.extend(tree_order)

        # 4. Only include escalation points where needed
        escalation_points = get_cross_scale_prerequisites(scale)
        curriculum.extend(escalation_points)

    return curriculum
```

### Benefits

1. **Appropriate Depth:** Students learn at the right level for the objective
2. **Reduced Cognitive Load:** Don't force quantum understanding for nomenclature
3. **Natural Modules:** Each scale + tree = coherent teaching unit
4. **Clear Escalation:** "Why" questions trigger controlled depth increase
5. **Multiple Entry Points:** Can start at any scale depending on prior knowledge

---

## Mapping to CHEM 361 Units

The existing course structure partially aligns:

| Course Unit | Primary Scale | Trees Covered |
|-------------|---------------|---------------|
| Coordination Chemistry | STRUCTURAL + ELECTRONIC | Coordination, CFT |
| Main Group Chemistry | DESCRIPTIVE | Main Group, Periodic Trends |
| Solid State Chemistry | STRUCTURAL | Crystal Structures |

### Recommended Adjustments

1. **Explicit Scale Labeling:** Tag each lecture with its scale
2. **Escalation Markers:** Note when and why we go deeper
3. **Tree Completion:** Finish one tree before starting another
4. **Scale-Appropriate Assessment:** Test at the taught scale, not deeper

---

## Visual Summary

```
╔═══════════════════════════════════════════════════════════════════════╗
║                    HIERARCHICAL KNOWLEDGE FOREST                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  SCALE 4   ┌─Atomic Structure──┐  ┌─Quantum Mechanics─┐               ║
║  QUANTUM   ├─Orbitals          │  ├─Wave functions    │               ║
║            └─Electron config   │  └─Spin              │               ║
║                    │                      │                            ║
║ ───────────────────┼──────────────────────┼─────────────────────────  ║
║                    ▼                      ▼                            ║
║  SCALE 3   ┌─Crystal Field─────┐  ┌─MO Theory─────────┐               ║
║  ELECTRON  ├─Octahedral        │  ├─σ/π bonding       │               ║
║            ├─Tetrahedral       │  └─MO diagrams       │               ║
║            └─CFSE              │                                       ║
║                    │                                                   ║
║ ───────────────────┼─────────────────────────────────────────────────  ║
║                    ▼                                                   ║
║  SCALE 2   ┌─Coordination Chem─┐  ┌─Crystal Structures┐               ║
║  STRUCT    ├─Nomenclature      │  ├─Unit cells        │               ║
║            ├─Isomerism         │  └─Packing           │               ║
║            └─Geometry          │                                       ║
║                    │                                                   ║
║ ───────────────────┼─────────────────────────────────────────────────  ║
║                    ▼                                                   ║
║  SCALE 1   ┌─Main Group────────┐  ┌─Transition Metals─┐               ║
║  DESCRIPT  ├─Alkali metals     │  ├─First row         │               ║
║            ├─Halogens          │  └─Properties        │               ║
║            └─Noble gases       │                                       ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║  NAVIGATION RULES:                                                     ║
║  • Stay within scale when possible                                     ║
║  • Explore tree siblings before escalating                             ║
║  • Escalate only when "why" requires it                               ║
║  • Blind path (→quantum) only for anomalies                           ║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

## Future Work

1. **Tag all 5,380 nodes** with scale and tree membership
2. **Implement scale-aware curriculum generator**
3. **Create escalation map** showing which topics trigger scale changes
4. **Validate with SLOs** - map each SLO to required scale depth
5. **Design assessments** that respect scale boundaries
6. **Compare with ACS guidelines** for inorganic chemistry

---

## References

- Hierarchical learning theory
- Coarse-graining in computational chemistry
- Levels of abstraction in computer science education
- Zone of proximal development (Vygotsky)

---

*Part of the Knowledge Graph Pedagogy Project*
*McNeese State University, CHEM 361*
*Insight documented: 2026-01-18, Session 4*
