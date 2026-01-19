# CHEM 361 Lecture Generation Framework
## Complete Package for LLM Analysis

**Purpose:** This document packages all framework components for analysis by Claude/ChatGPT.

**What we built:** A system to generate IC-level (Inorganic Chemistry) interactive lectures from textbook content via RAG, avoiding AI slop patterns.

---

# TABLE OF CONTENTS

1. [Overview & Architecture](#1-overview--architecture)
2. [Skills Framework](#2-skills-framework)
   - 2.1 generate-lecture.md
   - 2.2 verify-content.md
   - 2.3 create-diagrams.md
3. [Session 1 Outline (What Was Planned)](#3-session-1-outline)
4. [Session 1 Lecture (What Was Produced)](#4-session-1-lecture)
5. [Syllabus (Full Course Structure)](#5-syllabus)

---

# 1. Overview & Architecture

## The Problem

Standard AI-generated educational content has these issues:
- **AI slop patterns:** "Not X but Y", em-dashes for drama, "Let's explore", rhetorical questions
- **Bullet point syndrome:** Lists instead of narrative prose
- **Invented content:** Claims not grounded in actual textbooks
- **Generic diagrams:** Not based on real data

## The Solution

A framework that:
1. Queries a RAG system containing 8,756 chunks from 7 IC textbooks
2. Extracts actual textbook explanations
3. Rewrites in narrative prose (own voice, faithful to source)
4. Creates Canvas diagrams with cited data (Cordero 2008, Shannon 1976, NIST)
5. Verifies every claim against the textbook sources

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Outline (.md)  │────▶│  RAG Query      │────▶│  Narrative      │
│  What to cover  │     │  Qdrant + Ollama│     │  Writing        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
┌─────────────────┐     ┌─────────────────┐            │
│  Deploy to      │◀────│  Verify vs      │◀───────────┘
│  GitHub Pages   │     │  Sources        │
└─────────────────┘     └─────────────────┘
                               ▲
                               │
                        ┌──────┴──────┐
                        │ Canvas      │
                        │ Diagrams    │
                        └─────────────┘
```

## RAG System

| Setting | Value |
|---------|-------|
| Vector DB | Qdrant at localhost:6333 |
| Collection | `textbooks_chunks` (8,756 points) |
| Embedding | `nomic-embed-text:latest` (768-dim) |
| Textbooks | Atkins/Shriver, Housecroft, Basset, House, JD Lee |

---

# 2. Skills Framework

Skills are instruction files that codify the workflow for Claude Code.

---

## 2.1 generate-lecture.md

```markdown
---
name: generate-lecture
description: Generate IC-level interactive lectures from outlines using RAG textbook sources
trigger: When asked to create/generate a CHEM 361 lecture or session
---

# CHEM 361 Lecture Generation Framework

## Overview

Generate inorganic chemistry lectures that are:
- **Textbook-faithful**: Content drawn from Atkins, Housecroft, Basset, JD Lee, House
- **Narrative prose**: No bullet points, no AI patterns, storytelling approach
- **Interactive**: Canvas diagrams, hover effects, clickable periodic table
- **Verified**: Every claim traceable to RAG sources

---

## Workflow

1. Load Outline → 2. Query RAG → 3. Write Narrative → 4. Create Diagrams → 5. Verify → 6. Deploy

---

## Step 2: Query RAG for Each Topic

```python
import requests

QDRANT_URL = "http://localhost:6333"
OLLAMA_URL = "http://localhost:11434"
COLLECTION = "textbooks_chunks"

def embed(text):
    r = requests.post(f"{OLLAMA_URL}/api/embeddings", json={
        "model": "nomic-embed-text:latest",
        "prompt": text
    })
    return r.json()["embedding"]

def search(query, limit=5):
    vec = embed(query)
    r = requests.post(f"{QDRANT_URL}/collections/{COLLECTION}/points/search", json={
        "vector": {"name": "dense", "vector": vec},
        "limit": limit,
        "with_payload": True
    })
    return r.json()["result"]
```

---

## Step 3: Write Narrative Prose

### FORBIDDEN (AI Slop Patterns)

| Pattern | Example | Why Bad |
|---------|---------|---------|
| "Not X but Y" | "Not just four trends, but..." | Cliche framing |
| Em-dashes for drama | "The answer—surprisingly—is..." | Overused |
| Bullet points for content | "• First point • Second point" | Not narrative |
| "Let's explore" | "Let's explore why..." | Patronizing |
| "It's important to note" | "It's important to note that..." | Filler |
| Rhetorical questions | "But why does this happen?" | Cheap engagement |

### REQUIRED (Narrative Style)

```html
<!-- BAD: AI slop -->
<p>The lanthanide contraction is important because:</p>
<ul>
  <li>4f electrons shield poorly</li>
  <li>Zeff increases across the series</li>
</ul>

<!-- GOOD: Narrative prose -->
<p>The elements of the third transition series are preceded by the
lanthanoids, in which fourteen 4f electrons are added. These 4f orbitals
have poor shielding properties. The f electrons lie deep within the atom
and do not effectively screen outer electrons from the nuclear charge.</p>
```

### Voice Guidelines

- Write as if explaining to a bright student, not lecturing
- Use active voice: "The 6s orbital contracts" not "contraction is observed"
- Include historical context where relevant
- Use textbook phrasing, rephrased in own words (never copy-paste)

---

## Step 4: Create Diagrams

### Data Sources (MUST cite)

| Data Type | Source | Citation |
|-----------|--------|----------|
| Covalent radii | Cordero 2008 | Dalton Trans. 2008, 2832 |
| Ionic radii | Shannon 1976 | Acta Cryst. A32, 751 |
| Ionization energies | NIST ASD | physics.nist.gov |

---

## Quality Checklist

- [ ] No bullet points in content sections
- [ ] No AI slop patterns
- [ ] All data has source citations
- [ ] Narrative flows like textbook prose
- [ ] Verified against at least 2 RAG sources per major topic
```

---

## 2.2 verify-content.md

```markdown
---
name: verify-content
description: Verify lecture content against RAG textbook sources
trigger: When verifying CHEM 361 lecture claims or checking textbook fidelity
---

# Content Verification Skill

## Quick Verification Script

```bash
source /storage/RAG/.venv/bin/activate && python3 << 'EOF'
import requests

QDRANT_URL = "http://localhost:6333"
OLLAMA_URL = "http://localhost:11434"
COLLECTION = "textbooks_chunks"

def embed(text):
    r = requests.post(f"{OLLAMA_URL}/api/embeddings", json={
        "model": "nomic-embed-text:latest",
        "prompt": text
    })
    return r.json()["embedding"]

def search(query, limit=4):
    vec = embed(query)
    r = requests.post(f"{QDRANT_URL}/collections/{COLLECTION}/points/search", json={
        "vector": {"name": "dense", "vector": vec},
        "limit": limit,
        "with_payload": True
    })
    return r.json()["result"]

query = "YOUR TOPIC HERE"
results = search(query, 4)
for r in results:
    pdf = r["payload"].get("pdf_name", "unknown")
    text = r["payload"].get("text", "")[:600]
    print(f"\n[{pdf}]")
    print(text)
EOF
```

## Textbooks in RAG System

| PDF Name | Textbook |
|----------|----------|
| `Inorganic_Chemistry_Atkins_Shriver.pdf` | Atkins & Shriver |
| `ic_tina.pdf` | Housecroft & Sharpe |
| `ic_basset.pdf` | Basset |
| `descriptive_ic_house.pdf` | House |
| `concise_ic_jd_lee.pdf` | JD Lee |

## Red Flags (Content May Be Invented)

1. **No RAG hits**: Query returns low scores (<0.5) or unrelated content
2. **Contradicts sources**: Lecture says X, textbook says Y
3. **Too specific**: Exact numbers not found in any source
```

---

## 2.3 create-diagrams.md

```markdown
---
name: create-diagrams
description: Create Canvas-based chemistry diagrams for CHEM 361 lectures
trigger: When creating visualizations for IC lectures
---

# Chemistry Diagram Creation

## Template: Trend Plot with Real Data

```javascript
function drawAtomicRadiiTrend(canvasId) {
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');

    // real data from Cordero et al. 2008 (covalent radii in pm)
    const data = [
        { el: 'Li', Z: 3, r: 128 },
        { el: 'Be', Z: 4, r: 96 },
        // ... continue with real data
    ];

    // ALWAYS cite data source
    ctx.fillStyle = '#999';
    ctx.font = '10px monospace';
    ctx.fillText('Data: Cordero et al. 2008', 10, canvas.height - 10);
}
```

## Data Sources (ALWAYS CITE)

| Data | Source | Citation |
|------|--------|----------|
| Covalent radii | Cordero 2008 | Dalton Trans. 2008, 2832 |
| Ionic radii | Shannon 1976 | Acta Cryst. A32, 751 |
| Ionization energies | NIST ASD | physics.nist.gov |
```

---

# 3. Session 1 Outline (What Was Planned)

This is the input outline that guided lecture generation:

```markdown
# Session 1: The Periodic Table - Structure and Anomalies

## Learning Objectives
By the end of this session, students will be able to:
1. Explain effective nuclear charge (Zeff) and calculate it using Slater's rules
2. Predict atomic radius trends and explain anomalies (d-block, lanthanide contraction)
3. Describe relativistic effects and their chemical consequences (Au color, Hg liquid)
4. Explain the inert pair effect and predict oxidation state stability
5. Understand f-orbital behavior and why lanthanides have similar chemistry

## Topics

### Part 1: The Prediction Machine (Historical)
- Mendeleev's 1871 table
- Eka-aluminum prediction → Gallium discovery
- What the periodic law reveals

### Part 2: Effective Nuclear Charge
- Zeff = Z - σ
- Shielding and penetration
- Slater's rules with worked example (Cl)
- Why 2s penetrates more than 2p

### Part 3: Atomic Radii
- Definition (covalent radius)
- Period trend (decreasing left to right)
- Group trend (increasing down)
- Scandide contraction (3d poor shielding)

### Part 4: Lanthanide Contraction
- 4f electrons shield poorly
- Consequence: Zr ≈ Hf in radius
- Why separation is difficult
- Impact on 5d chemistry

### Part 5: Relativistic Effects
- Why heavy elements are different
- 6s contraction mechanism
- Why gold is golden (5d→6s transition in visible)
- Why mercury is liquid (6s² unavailable for bonding)

### Part 6: Inert Pair Effect
- ns² stabilization in heavy elements
- Pb(II) vs Pb(IV), Tl(I) vs Tl(III)
- Connection to relativistic effects

### Part 7: The f-Block
- 4f orbital burial
- Why lanthanides all behave as Ln(III)
- Gadolinium break

## Source Strategy
- Zeff, shielding: Atkins Chapter 1
- Anomalies, inert pair: Basset
- Lanthanide contraction: Housecroft
- Relativistic effects: Pyykkö 1988 review

## Visual Assets
- Interactive periodic table with electron configs
- Atomic radii trend diagram (Cordero 2008 data)
- Lanthanide ionic radii graph (Shannon 1976 data)
- Relativistic orbital comparison diagram
- f-orbital radial probability plot
```

---

# 4. Session 1 Lecture (What Was Produced)

The actual HTML lecture is 911 lines. Key sections:

## Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Session 1: The Periodic Table - CHEM 361</title>
    <style>
        :root {
            --text: #1a1a2e;
            --accent: #e94560;
        }
        /* narrative prose styling */
    </style>
</head>
<body>
    <header>
        <h1>Session 1: The Periodic Table</h1>
        <p>Structure, Trends, and Anomalies</p>
    </header>

    <main>
        <section id="mendeleev">
            <h2>The Prediction Machine</h2>
            <p>In 1871, Dmitri Mendeleev published a periodic table with
            gaps. Where others saw incompleteness, Mendeleev saw opportunity...</p>
            <!-- Mendeleev's prediction table -->
        </section>

        <section id="zeff">
            <h2>Effective Nuclear Charge</h2>
            <p>The field arising from a spherical distribution of charge
            is equivalent to the field generated by a single point charge
            at the center...</p>
            <!-- Slater's rules, worked example -->
        </section>

        <section id="radii">
            <h2>Atomic Radii</h2>
            <!-- Canvas diagram with Cordero 2008 data -->
        </section>

        <section id="lanthanide">
            <h2>The Lanthanide Contraction</h2>
            <p>The elements of the third transition series are preceded
            by the lanthanoids, in which fourteen 4f electrons are added.
            These 4f orbitals have poor shielding properties...</p>
            <!-- Shannon 1976 ionic radii graph -->
        </section>

        <section id="relativistic">
            <h2>Relativistic Effects</h2>
            <p>For light elements, relativistic corrections are negligible.
            For heavy elements with high atomic numbers, they become
            significant and can reduce atomic size by approximately
            20 percent...</p>
            <!-- Why Au is golden, Hg is liquid -->
        </section>

        <section id="inert-pair">
            <h2>The Inert Pair Effect</h2>
            <p>Carbon and silicon possess inner noble gas shells that
            efficiently screen their valence electrons from the nuclear
            charge. This promotes hybridization and bonding...</p>
        </section>

        <section id="fblock">
            <h2>The f-Block</h2>
            <!-- 4f burial, Gd break -->
        </section>
    </main>

    <footer>
        <h3>References</h3>
        <ul>
            <li>Atkins, P. & Shriver, D. Inorganic Chemistry. Oxford.</li>
            <li>Housecroft, C. & Sharpe, A. Inorganic Chemistry. Pearson.</li>
            <li>Cordero, B. et al. (2008) Dalton Trans. 2832.</li>
            <li>Shannon, R.D. (1976) Acta Cryst. A32, 751.</li>
            <li>Pyykkö, P. (1988) Chem. Rev. 88, 563.</li>
        </ul>
    </footer>

    <script>
        // Canvas diagrams with real data
        // Interactive periodic table
    </script>
</body>
</html>
```

## Sample Prose (Actual Output)

### Lanthanide Contraction Section

> The elements of the third transition series (period 6) are preceded by the lanthanoids, in which fourteen 4f electrons are added. These 4f orbitals have poor shielding properties. The f electrons lie deep within the atom and do not effectively screen outer electrons from the nuclear charge. As we cross from lanthanum to lutetium, Zeff experienced by the outer electrons increases steadily.
>
> The consequence is remarkable. Atomic radii in the 5d series are nearly identical to their congeners in the 4d series, even though period 6 atoms have 32 more electrons. Molybdenum and tungsten, separated by 32 protons and 32 electrons, have covalent radii of 154 and 162 pm respectively. Zirconium and hafnium both have radii of 175 pm.

### Relativistic Effects Section

> Mercury melts at −39°C, the only metal liquid at room temperature. The relativistic contraction of its 6s² electrons makes them unavailable for metallic bonding. The filled 5d¹⁰ shell contributes nothing to the metallic bond. With its bonding electrons contracted close to the nucleus and unwilling to overlap with neighboring atoms, mercury forms weak metallic bonds and melts at remarkably low temperature.

---

# 5. Syllabus (Full Course Structure)

33 sessions covering:

| Unit | Sessions | Topics |
|------|----------|--------|
| 1 | 1-5 | Periodic trends, symmetry, acids/bases |
| 2 | 6-12 | Coordination chemistry, CFT, mechanisms |
| 3 | 13-18 | Organometallics, catalysis |
| 4 | 19-22 | Bioinorganic chemistry |
| 5 | 23-28 | Main group chemistry |
| 6 | 29-32 | Materials, nanochemistry |
| 7 | 33 | Review |

Only Session 1 has been generated so far.

---

# Summary for Analysis

## What We Built

1. **Skills framework** - Codified methodology for lecture generation
2. **RAG integration** - Query 8,756 textbook chunks for faithful content
3. **Anti-AI-slop rules** - Explicit patterns to avoid
4. **Verification workflow** - Every claim traced to source
5. **One complete lecture** - Session 1: Periodic Table (911 lines HTML)

## Key Innovations

1. **Narrative prose requirement** - No bullet points in explanations
2. **Forbidden pattern list** - Concrete examples of AI slop to avoid
3. **Mandatory citations** - All data must have source (Cordero, Shannon, NIST)
4. **RAG verification** - Search textbooks before writing, verify after

## Files in This Package

| File | Purpose | Lines |
|------|---------|-------|
| `generate-lecture.md` | Main workflow skill | 344 |
| `verify-content.md` | Verification skill | 151 |
| `create-diagrams.md` | Diagram templates | 302 |
| `session_01_outline.md` | What was planned | ~200 |
| `session_01_periodic_trends.html` | What was produced | 911 |
| `SYLLABUS_CHEM361.md` | Full course structure | 322 |

---

*Package prepared for LLM analysis - January 2026*
