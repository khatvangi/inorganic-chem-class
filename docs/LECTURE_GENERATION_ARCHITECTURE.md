# Lecture Generation Architecture

**How LLM + Vector DB + Knowledge Funnel work together**

---

## The Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LECTURE GENERATION PIPELINE                        │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │  meta_book   │  Session 15: Crystal Field Theory
    │    .json     │  → concepts: [d-orbital splitting, Δo, spectrochemical series]
    │              │  → sources: {theory: atkins, examples: advanced, visuals: lee}
    └──────┬───────┘
           │
           ▼
    ┌──────────────────────────────────────────────────────────────────────┐
    │  1. EMBEDDING                                                         │
    │  ┌─────────────────────┐                                              │
    │  │ "d-orbital splitting│    Ollama           ┌──────────────────┐    │
    │  │  crystal field Δo   │ ──────────────────► │ 768-dim vector   │    │
    │  │  spectrochemical"   │   nomic-embed-text  │ [0.12, -0.34...] │    │
    │  └─────────────────────┘                     └──────────────────┘    │
    └──────────────────────────────────────────────────────────────────────┘
           │
           ▼
    ┌──────────────────────────────────────────────────────────────────────┐
    │  2. VECTOR SEARCH (Qdrant)                                            │
    │                                                                        │
    │  Collection: textbooks_chunks (8,753 points)                          │
    │  Vector: "dense" (768-dim, cosine similarity)                         │
    │                                                                        │
    │  Filter by pdf_name:                                                  │
    │    ├── Inorganic_Chemistry_Atkins_Shriver.pdf  → 2,494 chunks        │
    │    ├── advancex_ic_applicaionts.pdf            →   351 chunks        │
    │    └── concise_ic_jd_lee.pdf                   →   565 chunks        │
    │                                                                        │
    │  Returns: Top 20 chunks ranked by semantic similarity                 │
    └──────────────────────────────────────────────────────────────────────┘
           │
           ▼
    ┌──────────────────────────────────────────────────────────────────────┐
    │  3. KNOWLEDGE FUNNEL INTEGRATION                                      │
    │                                                                        │
    │  Query: /api/trace?q=crystal+field+theory                             │
    │                                                                        │
    │  Returns prerequisite graph:                                          │
    │    ├── QUANTUM (depth 3-4): atomic orbitals, electron config          │
    │    ├── ELECTRONIC (depth 1-2): MO theory, spectroscopy                │
    │    ├── STRUCTURAL (depth 2): coordination geometry, symmetry          │
    │    └── DESCRIPTIVE (depth 0): target concept                          │
    │                                                                        │
    │  Used for:                                                            │
    │    • Structuring lecture sections by scale                            │
    │    • "Bridge explanations" connecting prerequisites                   │
    │    • Quiz questions at different conceptual depths                    │
    └──────────────────────────────────────────────────────────────────────┘
           │
           ▼
    ┌──────────────────────────────────────────────────────────────────────┐
    │  4. LLM SYNTHESIS (Qwen3 via Ollama)                                  │
    │                                                                        │
    │  Input:                                                               │
    │    • Retrieved chunks from textbooks                                  │
    │    • Learning objectives from meta_book                               │
    │    • Prerequisite structure from Knowledge Funnel                     │
    │    • Scale classification (QUANTUM/ELECTRONIC/STRUCTURAL/DESCRIPTIVE) │
    │                                                                        │
    │  Prompts:                                                             │
    │    • Lecture: "Write full prose covering [concepts] using [chunks]"   │
    │    • Q&A: "Generate 25 questions at recall/application/analysis"      │
    │                                                                        │
    │  Output:                                                              │
    │    • Structured lecture content                                       │
    │    • Questions with explanations                                      │
    └──────────────────────────────────────────────────────────────────────┘
           │
           ▼
    ┌──────────────────────────────────────────────────────────────────────┐
    │  5. INTERACTIVE HTML GENERATION                                       │
    │                                                                        │
    │  Template features:                                                   │
    │    • ChemDoodle molecule viewers                                      │
    │    • Embedded quizzes with instant feedback                           │
    │    • Collapsible sections                                             │
    │    • Concept boxes color-coded by scale                               │
    │    • Source attribution tags                                          │
    │    • Link to Knowledge Funnel visualization                           │
    │    • Progress tracking                                                │
    └──────────────────────────────────────────────────────────────────────┘
```

---

## Component Roles

### 1. Qdrant Vector DB
**Purpose:** Semantic search over textbook content

| What It Stores | How It's Used |
|----------------|---------------|
| 8,753 text chunks | Find relevant passages for any concept |
| 768-dim embeddings | Semantic similarity (not keyword matching) |
| Metadata (pdf_name, tier) | Filter by specific textbook |

**Example query:**
```python
# "d-orbital splitting" → finds passages about CFT from Atkins, not just keyword matches
vector = embed("d-orbital splitting crystal field")
chunks = qdrant.query(vector, filter={"pdf_name": "Atkins"}, limit=10)
```

### 2. LLM (Qwen3)
**Purpose:** Synthesis and generation

| Task | Input | Output |
|------|-------|--------|
| Lecture writing | Chunks + objectives | Full prose content |
| Q&A generation | Chunks + concepts | MCQ with explanations |
| Knowledge extraction | Raw text | Topics, prerequisites |
| Bridge explanations | Two concepts | Connection text |

### 3. Knowledge Funnel
**Purpose:** Pedagogical structure

| Feature | How It Helps Lectures |
|---------|----------------------|
| Prerequisite graph | Know what to explain before CFT |
| Scale classification | Structure sections (QUANTUM→DESCRIPTIVE) |
| Concept depth | Place content at right level |
| Visual linking | Students see why they need each concept |

---

## Lecture Generation Flow (Detailed)

### Step 1: Load Session from Meta-Book
```python
session = {
    "topic": "Crystal Field Theory: octahedral",
    "scale": "ELECTRONIC",
    "key_concepts": ["d-orbital splitting", "Δo", "t2g/eg", "spectrochemical series"],
    "learning_objectives": [
        "Explain origin of crystal field splitting",
        "Order ligands by field strength"
    ],
    "sources": {
        "theory": "atkins",
        "examples": "advanced",
        "visuals": "lee"
    }
}
```

### Step 2: Query RAG for Content
```python
# Get embeddings
vector = embed(" ".join(session["key_concepts"]))

# Query each source textbook
chunks = []
for source in ["atkins", "advanced", "lee"]:
    pdf = SOURCE_MAP[source]  # e.g., "Inorganic_Chemistry_Atkins_Shriver.pdf"
    results = qdrant.query(
        vector=vector,
        filter={"pdf_name": pdf},
        using="dense",
        limit=8
    )
    chunks.extend(results)
```

### Step 3: Get Prerequisite Structure
```python
# Query Knowledge Funnel API
prereqs = requests.get("/api/trace?q=crystal+field+theory").json()

# Structure:
# {
#   "layers": {
#     "QUANTUM": ["Atomic Orbitals", "Electron Configuration"],
#     "ELECTRONIC": ["Crystal Field Theory", "MO Theory"],
#     "STRUCTURAL": ["Octahedral Geometry"],
#     "DESCRIPTIVE": ["Color of Complexes"]
#   }
# }
```

### Step 4: Generate Lecture with LLM
```python
prompt = f"""
Write a comprehensive lecture on: {session["topic"]}

Key concepts to cover:
{session["key_concepts"]}

Learning objectives:
{session["learning_objectives"]}

Prerequisite concepts (students should already know):
{prereqs["layers"]["QUANTUM"]}

Reference material from textbooks:
{chunks_text}

Structure the lecture by knowledge scale:
1. Connect to QUANTUM prerequisites (orbitals)
2. Build ELECTRONIC understanding (CFT core)
3. Link to STRUCTURAL context (geometry)
4. Reach DESCRIPTIVE outcomes (color, magnetism)
"""

lecture = ollama.generate(model="qwen3", prompt=prompt)
```

### Step 5: Generate Interactive HTML
```python
html = render_template(
    lecture_content=lecture,
    session=session,
    quiz_questions=generate_quiz(chunks, session),
    molecule_viewers=get_molecules(session),
    funnel_link=f"/visualizations/scales.html?q={session['topic']}"
)
```

---

## Q&A Generation Flow

### Difficulty Levels Mapped to Scale

| Difficulty | Scale | Question Type |
|------------|-------|---------------|
| Recall | DESCRIPTIVE | "What is the spectrochemical series?" |
| Application | STRUCTURAL/ELECTRONIC | "Calculate CFSE for d⁶ octahedral" |
| Analysis | QUANTUM/ELECTRONIC | "Explain why CO is strong field" |

### Generation Process
```python
for difficulty in ["recall", "application", "analysis"]:
    prompt = f"""
    Topic: {session["topic"]}
    Concepts: {session["key_concepts"]}
    Reference: {chunks_text}

    Generate {count} {difficulty} questions.
    Each question should:
    - Test genuine understanding
    - Include 4 options
    - Have detailed explanation
    - Tag the specific concept tested
    """

    questions = ollama.generate(prompt)
```

---

## Why This Architecture?

### Traditional Approach
```
Textbook → Read linearly → Hope students connect concepts
```

### Knowledge Funnel Approach
```
Student Question
       ↓
   Vector Search (find relevant content)
       ↓
   Knowledge Graph (find prerequisites)
       ↓
   LLM Synthesis (create coherent explanation)
       ↓
   Interactive Lecture (with embedded checks)
       ↓
   Visual Prerequisite Map (see the full picture)
```

### Benefits

| Component | Benefit |
|-----------|---------|
| **Vector DB** | Find semantically relevant content, not just keyword matches |
| **Knowledge Graph** | Know what students need before teaching new concept |
| **LLM** | Synthesize multiple textbook perspectives into one voice |
| **Scale Classification** | Structure content from fundamental to applied |
| **Interactive HTML** | Active learning with immediate feedback |

---

## Data Flow Diagram

```
                    ┌─────────────────┐
                    │   7 Textbooks   │
                    │   (8,753 chunks)│
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Qdrant Vector  │
                    │     Database    │
                    │   (768-dim)     │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Knowledge      │ │    Lecture      │ │      Q&A        │
│    Funnel       │ │   Generator     │ │   Generator     │
│   (5,380 nodes) │ │                 │ │                 │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         │          ┌────────▼────────┐          │
         │          │      LLM        │          │
         └─────────►│   (Qwen3)       │◄─────────┘
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Interactive    │
                    │     HTML        │
                    │   Lectures      │
                    └─────────────────┘
```

---

## Next Steps

1. **Generate all 33 sessions** using this pipeline
2. **Integrate funnel queries** into lecture structure
3. **Add adaptive paths** - skip prerequisites students know
4. **Deploy to chem361.thebeakers.com**

---

*Architecture designed for learner-centered, data-driven chemistry education*
