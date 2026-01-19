# Textbook Analysis: CHEM 361 Inorganic Chemistry

**Purpose:** Quantified analysis of 10 IC textbooks for conceptual density, topic coverage, and pedagogical quality.

---

## Textbooks Analyzed

| # | Textbook | Chunks | Focus |
|---|----------|--------|-------|
| 1 | Atkins/Shriver - Inorganic Chemistry | ~2,500 | Comprehensive theoretical |
| 2 | Housecroft/Sharpe (ic_tina.pdf) | ~2,400 | Balanced theory + descriptive |
| 3 | JD Lee - Concise IC | ~550 | Foundational, accessible |
| 4 | House - Descriptive IC | ~1,000 | Main group focus |
| 5 | Douglas/McDaniel (descriptive_ic.pdf) | ~1,500 | Descriptive emphasis |
| 6 | Basset - IC | ~450 | Compact reference |
| 7 | Advanced IC Applications | ~350 | Applications focus |
| 8 | Bertini - Bioinorganic | ~500 | Bioinorganic specialty |
| 9 | Saito - IC | ~400 | Alternative perspective |
| 10 | LibreTexts - IC | ~600 | Open educational resource |

---

## Analysis Dimensions

### 1. Topic Coverage (20 Topics)

Each textbook rated 1-5 on coverage of:

| Category | Topics |
|----------|--------|
| Fundamentals | Atomic Structure, MO Theory, Symmetry/Group Theory |
| Core IC | Acids & Bases, Redox, Coordination, Crystal Field Theory |
| Spectroscopy | UV-Vis, IR, NMR, Reaction Mechanisms |
| Descriptive | Main Group (s-block), Main Group (p-block), Transition Metals |
| Advanced | Lanthanides/Actinides, Organometallics, Bioinorganic |
| Applications | Solid State, Catalysis, Materials, Environmental, Medicinal |

**Rating Scale:**
- 5 (excellent): Comprehensive, multiple chapters, derivations
- 4 (good): Solid coverage, one chapter, worked examples
- 3 (fair): Basic coverage, partial chapter
- 2 (limited): Mentioned but not developed
- 1 (absent): Not covered

### 2. Worked Examples (Quantified)

Not "many" or "few" - actual counts:
- Total examples per book
- Distribution by difficulty (basic/intermediate/advanced)
- Distribution by topic
- Average steps per example

### 3. Conceptual Density

| Metric | Description | Range |
|--------|-------------|-------|
| Thread completeness | Does passage complete conceptual chain? | 0-1 |
| Integration points | Prior concepts needed to understand | count |
| Derivation ratio | Fraction of equations derived vs stated | 0-1 |
| Figure integration | Are figures explained in text? | 0-1 |

**Composite density** = (thread × derivation × figure) / 3

### 4. Visual Analysis

Counts by type:
- MO diagrams
- Crystal structures
- Reaction schemes
- Energy level diagrams
- Periodic trend plots
- 3D molecular structures
- Phase diagrams
- Spectroscopic data
- Data tables

### 5. Pedagogy Metrics

| Metric | Description |
|--------|-------------|
| Scaffolding (1-5) | Does each concept build on named prior? |
| Misconceptions addressed | Does text address common errors? |
| Review elements | Summary boxes, key equations, objectives |
| Prior knowledge assumed | What's assumed but not reviewed |

---

## Results

*Analysis in progress. Results will be populated from `textbook_analysis_v2.json` when complete.*

### Comparison Matrix (Placeholder)

| Book | Chunks | MO | CFT | Coord | Density | Examples | Scaffolding | Overall |
|------|--------|----|----|-------|---------|----------|-------------|---------|
| Atkins | 2494 | - | - | - | - | - | - | - |
| Housecroft | 2375 | - | - | - | - | - | - | - |
| JD Lee | 565 | - | - | - | - | - | - | - |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

---

## Hub-to-Textbook Mapping

For each hub concept, which textbook provides best coverage?

| Hub | Best Textbook | Rating | Notes |
|-----|---------------|--------|-------|
| Crystal Field Theory | Atkins | TBD | |
| MO Theory | Atkins | TBD | |
| Acid-Base Chemistry | TBD | TBD | |
| Redox Chemistry | TBD | TBD | |
| Periodic Trends | TBD | TBD | |

---

## Foundation Coverage

Do all textbooks cover the 32 actionable foundations?

| Foundation | Atkins | Housecroft | JD Lee | House | Basset |
|------------|--------|------------|--------|-------|--------|
| Coordination Chem Fundamentals | ✓ | ✓ | ✓ | ✓ | ✓ |
| Electron Configuration | ✓ | ✓ | ✓ | ✓ | ✓ |
| Oxidation States | ✓ | ✓ | ✓ | ✓ | ✓ |
| Group Theory Basics | ✓ | ✓ | ✗ | ✗ | ✗ |

*Full table from Task 2 analysis*

---

## Methodology

**Script:** `experiments/analyze_textbooks_v2.py`

**Process:**
1. Retrieve chunks from Qdrant (`textbooks_chunks` collection)
2. For each book, analyze 500 chunks across 5 dimensions
3. Use Qwen3 LLM for structured extraction
4. Aggregate results and compute composites
5. Generate comparison matrix

**Output Files:**
- `experiments/results/textbook_analysis_v2.json` - Full results
- `experiments/results/textbook_comparison_matrix.json` - Matrix data
- `experiments/results/textbook_comparison_matrix.md` - Formatted table

---

## Usage in Curriculum Design

1. **Topic not covered well?** → Check which textbook has best rating
2. **Need worked examples?** → Use textbook with highest example count for that topic
3. **Need derivations?** → Use textbook with highest derivation ratio
4. **Teaching a hub concept?** → Use best-rated textbook for that hub

---

*Analysis started: 2026-01-19*
*Status: In progress (Book 1/10, Phase 2/5)*
*Estimated completion: 6-7 hours*
