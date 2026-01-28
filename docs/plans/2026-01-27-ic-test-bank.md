# IC Test Bank Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a complete inorganic chemistry test bank — one interactive HTML page per topic — using the approved `quantum_numbers.html` format, with inline textbook figures and questions sourced from 7 books in Qdrant.

**Architecture:** Each topic gets its own self-contained HTML file in `testbank/`. Every file uses the same CSS/JS template (extracted from the approved prototype), same typography (Crimson Pro + Source Sans 3 + JetBrains Mono), same warm book aesthetic. Questions are hand-written (Claude-generated) referencing Qdrant content and paired with extracted Housecroft figures. A `testbank/index.html` hub page links to all topics.

**Tech Stack:** Vanilla HTML/CSS/JS (no build). Housecroft figures already extracted as PNGs. ChemDoodle Web Components for molecular visualization (topics 5+). Qdrant (localhost:6333) for question source material.

---

## Approved Design Specification

The approved prototype is `testbank/quantum_numbers.html` (1017 lines). Key design elements:

### Visual Design
- **Background:** `#faf8f4` (warm off-white)
- **Typography:** Crimson Pro 18px body (serif), Source Sans 3 (headings/UI), JetBrains Mono (numbers/code)
- **Colors:** accent `#b44a1e` (burnt orange), teal `#1a5c5a`, warm grays
- **Card style:** white `#fff` with `1px solid #e0dbd3` border, `12px` border-radius, subtle shadow
- **Max width:** 780px centered

### Question Block Structure
```html
<div class="q-block" data-answer="B">
    <div class="q-source">
        <span>Housecroft & Sharpe, Fig. X.Y</span>
        <span class="book-tag">HOUSECROFT</span>
    </div>
    <div class="q-body">
        <figure class="q-figure">
            <img src="../assets/figures/chapterN/fig_N_M.png" alt="...">
            <figcaption>Fig. X.Y — Description</figcaption>
        </figure>
        <div class="q-num">Q1</div>
        <p class="q-stem">Question text...</p>
        <ul class="q-options">
            <li data-val="A"><span class="opt-letter">a</span> Option text</li>
            <!-- ... -->
        </ul>
        <button class="q-reveal-btn" onclick="revealAnswer(this)">Show Answer</button>
        <div class="q-answer">
            <div class="answer-label">Answer: (b)</div>
            <p>Explanation...</p>
        </div>
    </div>
</div>
```

### Interaction
- Click option → auto-reveals answer (correct = green, wrong = pink, correct highlighted)
- "Show Answer" button for study mode (reveals without answering)
- Score pill in sticky topbar: `correct / total_answered`
- Final score summary card when all answered
- Reset button to retry

### Section Organization
- 3-5 sections per topic, 3-5 questions per section
- Each section has `<div class="section-head">` with title + question range
- Total: ~15 questions per topic

### Source Attribution
- Every question has a `.q-source` bar with book name + chapter/figure reference
- Book tag pill: `HOUSECROFT`, `ATKINS`, `JD LEE`, `BASSET`, etc.
- Questions without figures still have the source bar (just no `<figure>`)

---

## Topics & Figures Inventory

### Available Resources

**Qdrant books (textbooks_chunks collection):**
| Book | Chunks | Key |
|------|--------|-----|
| Atkins & Shriver | 2,494 | `Inorganic_Chemistry_Atkins_Shriver.pdf` |
| Housecroft (ic_tina) | 2,375 | `ic_tina.pdf` |
| Descriptive IC | 1,495 | `descriptive_ic.pdf` |
| House (Descriptive IC) | 1,027 | `descriptive_ic_house.pdf` |
| JD Lee (Concise IC) | 565 | `concise_ic_jd_lee.pdf` |
| Basset (Advanced IC) | 446 | `ic_basset.pdf` |
| Advanced IC Applications | 351 | `advancex_ic_applicaionts.pdf` |

**Extracted Housecroft figures (by chapter):**
| Ch | Topic | Figures |
|----|-------|---------|
| 1 | Atomic structure | 22 |
| 2 | Bonding (MO theory) | 29 |
| 3 | Symmetry | 35 |
| 4 | Solid state | 73 |
| 5 | Acids & bases | 16 |
| 6 | Redox | 21 |
| 7 | Non-aqueous solvents | 7 |
| 8 | Metallic bonding & alloys | 58 |
| 9 | Group 1 | 16 |
| 10 | Group 2 | 14 |
| 11 | Group 13 | 15 |
| 12 | Group 14 | 8 |
| 13 | Groups 15/16 | 14 |
| 14 | Group 17 (halogens) | 21 |
| 15 | Group 18 | 7 |
| 16 | Transition metals intro | 5 |
| 17 | d-block (1st row) | 15 |
| 20 | d-block (2nd/3rd row) | 45 |
| 21 | Coordination chemistry | 24 |
| 22 | Ligand field theory | 27 |
| 23 | Spectroscopy | 21 |
| 24 | Organometallics | 102 |
| 26 | Catalysis | 69 |

---

## Topic Files to Create

Each file follows the same template. Topics are ordered by CHEM 361 curriculum sequence.

| # | File | Topic | Sections | Housecroft Ch | Figures | ChemDoodle? |
|---|------|-------|----------|---------------|---------|-------------|
| 1 | `quantum_numbers.html` | Quantum Numbers & Atomic Orbitals | 4 | Ch 1 | 12 used | No |
| 2 | `electron_configuration.html` | Electron Configuration & Periodic Properties | 4 | Ch 1 | 6 | No |
| 3 | `mo_theory.html` | Molecular Orbital Theory | 4 | Ch 2 | 12 | No |
| 4 | `bond_properties.html` | Bond Order, Length & Enthalpy | 3 | Ch 2 | 6 | No |
| 5 | `symmetry.html` | Molecular Symmetry & Point Groups | 4 | Ch 3 | 10 | Yes |
| 6 | `solid_state.html` | Solid State & Crystal Structures | 4 | Ch 4 | 15 | Yes |
| 7 | `acids_bases.html` | Acids, Bases & Solvents | 3 | Ch 5, 7 | 8 | No |
| 8 | `redox.html` | Redox Chemistry & Electrochemistry | 3 | Ch 6 | 8 | No |
| 9 | `coordination.html` | Coordination Chemistry | 4 | Ch 21 | 10 | Yes |
| 10 | `isomerism.html` | Isomerism in Coordination Compounds | 3 | Ch 21 | 6 | Yes |
| 11 | `crystal_field.html` | Crystal Field Theory & Ligand Field Theory | 4 | Ch 22 | 12 | No |
| 12 | `spectroscopy.html` | Electronic Spectroscopy & Magnetism | 3 | Ch 23 | 8 | No |
| 13 | `organometallics.html` | Organometallic Chemistry | 4 | Ch 24 | 15 | Yes |
| 14 | `catalysis.html` | Homogeneous & Heterogeneous Catalysis | 3 | Ch 26 | 10 | Yes |
| 15 | `descriptive_main.html` | Descriptive Chemistry (Main Group) | 4 | Ch 9-15 | 10 | No |
| 16 | `descriptive_tm.html` | Descriptive Chemistry (Transition Metals) | 4 | Ch 16-17, 20 | 10 | No |
| 17 | `nomenclature.html` | IUPAC Nomenclature | 3 | Ch 21, 24 | 4 | Yes |

**Total: 17 topics, ~255 questions, ~170 figures**

---

## Tasks

### Task 1: Extract shared CSS/JS template

**Files:**
- Create: `testbank/testbank-base.css`
- Create: `testbank/testbank-base.js`

**Step 1:** Extract the `<style>` block (lines 10-375 of `quantum_numbers.html`) into `testbank/testbank-base.css`. No modifications needed — it's the approved design.

**Step 2:** Extract the `<script>` block (lines 936-1013 of `quantum_numbers.html`) into `testbank/testbank-base.js`. No modifications needed.

**Step 3:** Refactor `quantum_numbers.html` to link to these external files instead of inline:
```html
<link rel="stylesheet" href="testbank-base.css">
<!-- ... at bottom ... -->
<script src="testbank-base.js"></script>
```

**Step 4:** Verify `quantum_numbers.html` still works in browser after refactoring.

**Step 5:** Commit.
```bash
git add testbank/testbank-base.css testbank/testbank-base.js testbank/quantum_numbers.html
git commit -m "refactor: extract shared test bank CSS/JS template"
```

---

### Task 2: Create test bank hub page

**Files:**
- Create: `testbank/index.html`

**Step 1:** Create `testbank/index.html` with links to all 17 topic pages. Use same warm aesthetic. Organized by unit:
- **Unit 1 — Foundations:** Quantum Numbers, Electron Configuration, MO Theory, Bond Properties
- **Unit 2 — Molecular Properties:** Symmetry, Acids & Bases, Redox
- **Unit 3 — Coordination Chemistry:** Coordination, Isomerism, Crystal Field, Spectroscopy
- **Unit 4 — Advanced Topics:** Organometallics, Catalysis, Nomenclature
- **Unit 5 — Descriptive Chemistry:** Main Group, Transition Metals, Solid State

Each link shows: topic name, question count, and a progress indicator (localStorage-based, shows how many answered).

**Step 2:** Add link from main `index.html` to `testbank/index.html`:
```html
<a href="testbank/" class="nav-link featured">
    <span class="chapter">TB</span>
    <span>Test Bank (17 Topics, 255+ Questions)</span>
</a>
```

**Step 3:** Commit.

---

### Task 3: Electron Configuration & Periodic Properties

**Files:**
- Create: `testbank/electron_configuration.html`

**Sections (15 questions):**
1. **Aufbau Principle & Filling Order** (Q1-4) — Madelung rule, aufbau exceptions (Cr, Cu), Hund's rule
2. **Electron Configurations of Ions** (Q5-8) — d-block ions (lose 4s before 3d), lanthanide/actinide configs
3. **Effective Nuclear Charge & Shielding** (Q9-11) — Slater's rules calculations, Z_eff trends
4. **Periodic Trends** (Q12-15) — IE anomalies (N>O, Be>B), EA trends, atomic/ionic radii

**Figures to use:** `chapter1/` — fig_1_19 (energy levels), fig_1_20 (aufbau), fig_1_21 (periodic table), fig_1_22 (electron configs), fig_1_24 (radii), fig_1_26 (IE)

**Qdrant sources:** Atkins Ch 1, Housecroft Ch 1, JD Lee Ch 2-3

**Step 1:** Write all 15 questions in HTML using the template structure.

**Step 2:** Verify in browser — all figures load, interactions work.

**Step 3:** Commit.

---

### Task 4: MO Theory

**Files:**
- Create: `testbank/mo_theory.html`

**Sections (15 questions):**
1. **LCAO & MO Basics** (Q1-3) — constructive/destructive interference, bonding vs antibonding, bond order formula
2. **Homonuclear Diatomics** (Q4-8) — H2 through F2 MO diagrams, s-p mixing, O2 paramagnetism, PES of N2
3. **Heteronuclear Diatomics** (Q9-12) — HF, CO, ICl MO diagrams, electronegativity and orbital mixing
4. **Applications & Frontier Orbitals** (Q13-15) — CO as ligand, HOMO/LUMO, Walsh diagram concepts

**Figures to use:** `chapter2/` — fig_2_1 (VSEPR), fig_2_8-2_10 (interference, H2 MO), fig_2_11 (PES N2), fig_2_12-2_19 (homonuclear MO diagrams), fig_2_20-2_24 (heteronuclear MO)

**Qdrant sources:** Atkins Ch 2, Housecroft Ch 2, JD Lee Ch 4

**Step 1:** Write all 15 questions.

**Step 2:** Verify in browser.

**Step 3:** Commit.

---

### Task 5: Bond Properties

**Files:**
- Create: `testbank/bond_properties.html`

**Sections (12 questions):**
1. **Bond Order from MO Diagrams** (Q1-4) — calculate BO for O2, O2+, O2-, N2, NO, CO
2. **Bond Length & Bond Enthalpy Correlations** (Q5-8) — order by length, predict from BO, anomalies
3. **Bond Character: Ionic, Covalent, Metallic** (Q9-12) — Ketelaar triangle, Fajans' rules, polarization

**Figures to use:** `chapter2/` — fig_2_25-2_28 (bond correlations, Ketelaar triangle)

**Qdrant sources:** Atkins Ch 2, Housecroft Ch 2, JD Lee Ch 3

**Step 1:** Write all 12 questions.

**Step 2:** Verify in browser.

**Step 3:** Commit.

---

### Task 6: Molecular Symmetry

**Files:**
- Create: `testbank/symmetry.html`

**Sections (15 questions):**
1. **Symmetry Elements & Operations** (Q1-4) — identify C_n axes, sigma planes, i, S_n in given molecules
2. **Point Group Assignment** (Q5-8) — flowchart application: H2O (C2v), NH3 (C3v), BF3 (D3h), benzene (D6h)
3. **Character Tables & Representations** (Q9-12) — read character tables, identify irreducible representations, determine IR/Raman activity
4. **Applications to Bonding** (Q13-15) — symmetry-adapted linear combinations, predicting orbital symmetry labels

**Figures to use:** `chapter3/` — point group flowchart, symmetry elements, character tables

**ChemDoodle:** 3D molecule viewer for identifying symmetry elements (e.g., rotate H2O, see C2 axis)

**Qdrant sources:** Atkins Ch 3, Housecroft Ch 3

**Step 1:** Write all 15 questions. For ChemDoodle questions, include a `<div id="chemdoodle-qN">` container with setup script.

**Step 2:** Verify in browser.

**Step 3:** Commit.

---

### Task 7: Solid State

**Files:**
- Create: `testbank/solid_state.html`

**Sections (15 questions):**
1. **Unit Cells & Lattice Types** (Q1-4) — 7 crystal systems, 14 Bravais lattices, counting atoms in unit cell
2. **Close-Packed Structures** (Q5-8) — ccp vs hcp, coordination numbers, packing efficiency, ABCABC vs ABAB
3. **Ionic Structures** (Q9-12) — NaCl, CsCl, ZnS types, radius ratio rules, Madelung constant
4. **Band Theory & Properties** (Q13-15) — metals vs insulators vs semiconductors, band gap, doping

**Figures to use:** `chapter4/` — unit cells, close-packed layers, ionic structures, band diagrams

**ChemDoodle:** 3D crystal structure viewer for unit cells

**Qdrant sources:** Atkins Ch 4, Housecroft Ch 4, House Ch 1-3

**Step 1:** Write all 15 questions.

**Step 2:** Verify in browser.

**Step 3:** Commit.

---

### Task 8: Acids, Bases & Solvents

**Files:**
- Create: `testbank/acids_bases.html`

**Sections (12 questions):**
1. **Bronsted & Lewis Definitions** (Q1-4) — classify acids/bases, identify conjugate pairs, Lewis acid/base in TM chemistry
2. **Hard-Soft Acid-Base Theory** (Q5-8) — HSAB classification, predict preferred ligand, explain stability trends
3. **Non-Aqueous Solvents** (Q9-12) — liquid ammonia, SO2, superacids, leveling effect

**Figures to use:** `chapter5/` — HSAB table, acid-base equilibria; `chapter7/` — solvent properties

**Qdrant sources:** Atkins Ch 5, Housecroft Ch 5 & 7, JD Lee Ch 6

**Step 1:** Write all 12 questions.

**Step 2:** Verify in browser.

**Step 3:** Commit.

---

### Task 9: Redox Chemistry

**Files:**
- Create: `testbank/redox.html`

**Sections (12 questions):**
1. **Standard Reduction Potentials** (Q1-4) — read E° table, predict spontaneity, Nernst equation applications
2. **Latimer & Frost Diagrams** (Q5-8) — read Latimer diagrams, determine disproportionation, Frost diagram analysis
3. **Pourbaix Diagrams & Electrochemistry** (Q9-12) — pH-potential diagrams, corrosion, Ellingham diagrams

**Figures to use:** `chapter6/` — Latimer diagrams, Frost diagrams, Pourbaix diagrams, Ellingham diagrams

**Qdrant sources:** Atkins Ch 6, Housecroft Ch 6, JD Lee Ch 7

**Step 1:** Write all 12 questions.

**Step 2:** Verify in browser.

**Step 3:** Commit.

---

### Task 10: Coordination Chemistry

**Files:**
- Create: `testbank/coordination.html`

**Sections (15 questions):**
1. **Werner's Theory & Terminology** (Q1-4) — coordination number, geometry, denticity, chelate effect
2. **Nomenclature** (Q5-8) — name complex ions, formula from name, bridging/ambidentate ligands
3. **Coordination Geometries** (Q9-12) — tetrahedral vs square planar, factors determining geometry, Jahn-Teller
4. **Stability & Formation Constants** (Q13-15) — stepwise vs overall, Irving-Williams series, chelate/macrocyclic effect

**Figures to use:** `chapter21/` — coordination geometries, chelate rings, crystal structures

**ChemDoodle:** 3D complex viewer (e.g., rotate [Co(NH3)6]3+)

**Qdrant sources:** Atkins Ch 7-8, Housecroft Ch 21, JD Lee Ch 8

**Step 1:** Write all 15 questions.

**Step 2:** Verify in browser.

**Step 3:** Commit.

---

### Task 11: Isomerism

**Files:**
- Create: `testbank/isomerism.html`

**Sections (12 questions):**
1. **Structural Isomerism** (Q1-4) — ionization, hydrate, linkage, coordination isomers
2. **Geometric Isomerism** (Q5-8) — cis/trans, fac/mer, identify from formula
3. **Optical Isomerism** (Q9-12) — enantiomers, Delta/Lambda notation, resolve racemic mixtures

**Figures to use:** `chapter21/` — isomer diagrams, mirror images

**ChemDoodle:** 3D viewer for cis vs trans, Delta vs Lambda

**Qdrant sources:** Atkins Ch 8, Housecroft Ch 21

**Step 1:** Write all 12 questions.

**Step 2:** Verify in browser.

**Step 3:** Commit.

---

### Task 12: Crystal Field Theory & Ligand Field Theory

**Files:**
- Create: `testbank/crystal_field.html`

**Sections (15 questions):**
1. **CFT Basics** (Q1-4) — d-orbital splitting in Oh and Td, 10Dq, factors affecting delta (spectrochemical series)
2. **High Spin vs Low Spin** (Q5-8) — predict spin state, calculate CFSE, pairing energy vs delta
3. **Tanabe-Sugano Diagrams** (Q9-12) — read T-S diagrams, identify ground term, predict transitions
4. **Jahn-Teller & Structural Effects** (Q13-15) — tetragonal distortion, elongation vs compression, d4 and d9 cases

**Figures to use:** `chapter22/` — d-orbital splitting, spectrochemical series, Tanabe-Sugano diagrams, CFSE trends

**Qdrant sources:** Atkins Ch 20, Housecroft Ch 22, JD Lee Ch 22

**Step 1:** Write all 15 questions.

**Step 2:** Verify in browser.

**Step 3:** Commit.

---

### Task 13: Electronic Spectroscopy & Magnetism

**Files:**
- Create: `testbank/spectroscopy.html`

**Sections (12 questions):**
1. **Term Symbols & Microstates** (Q1-4) — derive ground state term, Hund's rules, Russell-Saunders coupling
2. **Selection Rules & UV-Vis** (Q5-8) — Laporte rule, spin selection rule, d-d band assignment
3. **Magnetism** (Q9-12) — spin-only formula, calculate mu_eff, paramagnetic vs diamagnetic, ferromagnetism

**Figures to use:** `chapter23/` — UV-Vis spectra, Orgel diagrams, magnetic susceptibility plots

**Qdrant sources:** Atkins Ch 20, Housecroft Ch 23

**Step 1:** Write all 12 questions.

**Step 2:** Verify in browser.

**Step 3:** Commit.

---

### Task 14: Organometallic Chemistry

**Files:**
- Create: `testbank/organometallics.html`

**Sections (15 questions):**
1. **18-Electron Rule & Electron Counting** (Q1-4) — CBC vs ionic model, count electrons for Fe(CO)5, Cr(C6H6)2
2. **Metal Carbonyls & Bonding** (Q5-8) — CO stretching frequencies, back-bonding, isolobal analogy
3. **Common Reactions** (Q9-12) — oxidative addition, reductive elimination, migratory insertion, beta-hydride elimination
4. **Pi-Bonded Ligands** (Q13-15) — metallocenes, alkene complexes, Dewar-Chatt-Duncanson model

**Figures to use:** `chapter24/` — molecular structures, MO diagrams, reaction mechanisms

**ChemDoodle:** 3D organometallic structures (ferrocene, Cr(CO)6)

**Qdrant sources:** Atkins Ch 22, Housecroft Ch 24, Advanced IC Applications

**Step 1:** Write all 15 questions.

**Step 2:** Verify in browser.

**Step 3:** Commit.

---

### Task 15: Catalysis

**Files:**
- Create: `testbank/catalysis.html`

**Sections (12 questions):**
1. **Homogeneous Catalysis** (Q1-4) — Wilkinson's catalyst, Wacker process, olefin metathesis (Grubbs)
2. **Heterogeneous Catalysis** (Q5-8) — Haber-Bosch, Fischer-Tropsch, surface adsorption, Langmuir isotherm
3. **Catalytic Cycles & Green Chemistry** (Q9-12) — identify elementary steps in cycles, turnover number/frequency, asymmetric catalysis

**Figures to use:** `chapter26/` — catalytic cycles, energy profiles, surface structures

**ChemDoodle:** catalyst structures

**Qdrant sources:** Atkins Ch 25-26, Housecroft Ch 26-27

**Step 1:** Write all 12 questions.

**Step 2:** Verify in browser.

**Step 3:** Commit.

---

### Task 16: Descriptive Chemistry — Main Group

**Files:**
- Create: `testbank/descriptive_main.html`

**Sections (15 questions):**
1. **Groups 1 & 2** (Q1-4) — diagonal relationships, flame colors, solubility trends, anomalous Li/Be
2. **Groups 13 & 14** (Q5-8) — boron hydrides (Wade's rules), inert pair effect, allotropes of carbon/silicon
3. **Groups 15 & 16** (Q9-12) — nitrogen oxides, phosphorus allotropes, sulfur chemistry, hypervalency
4. **Groups 17 & 18** (Q13-15) — interhalogen compounds, pseudohalogens, noble gas chemistry (XeF2, XeF4)

**Figures to use:** `chapter9/`-`chapter15/` figures, structures of molecules

**Qdrant sources:** Housecroft Ch 9-15, JD Lee Ch 9-18, House, Descriptive IC

**Step 1:** Write all 15 questions.

**Step 2:** Verify in browser.

**Step 3:** Commit.

---

### Task 17: Descriptive Chemistry — Transition Metals

**Files:**
- Create: `testbank/descriptive_tm.html`

**Sections (15 questions):**
1. **First Row Overview** (Q1-4) — oxidation states, aqua ion colors, trends across Ti-Cu
2. **Second & Third Row** (Q5-8) — comparison with 1st row, relativistic effects, lanthanide contraction effects
3. **Key Compounds & Reactions** (Q9-12) — permanganate, dichromate, Ti/V/Cr/Mn/Fe/Co/Ni/Cu chemistry
4. **Lanthanides & Actinides** (Q13-15) — f-orbital participation, magnetic properties, nuclear applications

**Figures to use:** `chapter16/`, `chapter17/`, `chapter20/` — oxidation state diagrams, color photographs, structural data

**Qdrant sources:** Housecroft Ch 16-17, 20, 23; Atkins Ch 19; JD Lee Ch 19-26

**Step 1:** Write all 15 questions.

**Step 2:** Verify in browser.

**Step 3:** Commit.

---

### Task 18: IUPAC Nomenclature

**Files:**
- Create: `testbank/nomenclature.html`

**Sections (12 questions):**
1. **Coordination Compound Names** (Q1-4) — name from formula, formula from name, stock notation
2. **Ligand Names & Prefixes** (Q5-8) — bis/tris vs di/tri, ambidentate ligands, bridging nomenclature
3. **Organometallic & Special Cases** (Q9-12) — hapto notation, kappa notation, IUPAC 2005 rules

**Figures to use:** minimal (nomenclature is mostly textual), but include structures for "name this complex" questions

**ChemDoodle:** display 3D structure, ask student to name it

**Qdrant sources:** Atkins appendix, Housecroft Ch 21 & 24

**Step 1:** Write all 12 questions.

**Step 2:** Verify in browser.

**Step 3:** Commit.

---

### Task 19: Update hub page with completion tracking

**Files:**
- Modify: `testbank/index.html`
- Modify: `testbank/testbank-base.js`

**Step 1:** Add localStorage-based tracking to `testbank-base.js`:
- After each answer, save progress to `localStorage` keyed by topic slug
- Format: `testbank_<slug>: { answered: N, correct: M, total: T }`

**Step 2:** Update `testbank/index.html` to read progress from localStorage and display:
- Green check for completed topics (all questions answered)
- Progress bar or fraction for partially completed
- Total score across all topics

**Step 3:** Commit.

---

### Task 20: Final integration & git push

**Files:**
- Modify: `index.html` (main site)

**Step 1:** Add prominent test bank link to main site index.html:
```html
<a href="testbank/" class="nav-link featured" style="background: linear-gradient(135deg, rgba(180, 74, 30, 0.15), rgba(26, 92, 90, 0.12)); border-color: rgba(180, 74, 30, 0.4);">
    <span class="chapter" style="color: #b44a1e;">TB</span>
    <span>Interactive Test Bank (17 Topics)</span>
</a>
```

**Step 2:** Verify all pages load at `chem361.thebeakers.com/testbank/`.

**Step 3:** Final commit and push.
```bash
git add -A testbank/ index.html
git commit -m "feat: complete IC test bank — 17 topics, 255+ questions"
git push
```

---

## ChemDoodle Integration Notes

For topics requiring molecular visualization (Tasks 6, 7, 10, 11, 14, 15, 18):

**Include in `<head>`:**
```html
<script src="https://web.chemdoodle.com/assets/ChemDoodleWeb.js"></script>
<link rel="stylesheet" href="https://web.chemdoodle.com/assets/ChemDoodleWeb.css">
```

**Usage pattern for 3D structures:**
```html
<div id="chemdoodle-q5" style="width:340px; height:260px; margin:0 auto 1rem;"></div>
<script>
const viewer = new ChemDoodle.TransformCanvas3D('chemdoodle-q5', 340, 260);
viewer.styles.set3DRepresentation('Ball and Stick');
const mol = ChemDoodle.readMOL('...mol data...');
viewer.loadMolecule(mol);
</script>
```

Only use ChemDoodle where 3D visualization genuinely helps the question — don't force it. Many coordination chemistry questions work fine with static 2D figures from the textbook.

---

## Execution Order

**Phase 1 — Template & Hub (Tasks 1-2):** Extract shared CSS/JS, build hub page.

**Phase 2 — Unit 1 (Tasks 3-5):** Electron config, MO theory, bond properties (build on existing Ch 1-2 figures).

**Phase 3 — Unit 2 (Tasks 6-9):** Symmetry, solid state, acids/bases, redox.

**Phase 4 — Unit 3 (Tasks 10-13):** Coordination, isomerism, CFT, spectroscopy.

**Phase 5 — Unit 4 (Tasks 14-18):** Organometallics, catalysis, descriptive chem, nomenclature.

**Phase 6 — Polish (Tasks 19-20):** Progress tracking, final integration.
