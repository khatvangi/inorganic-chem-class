# Lecture Generation Framework

**CHEM 361 Inorganic Chemistry - Interactive Lecture System**

---

## Overview

This framework generates interactive HTML lectures from course outlines using textbook content from a RAG (Retrieval-Augmented Generation) system. The output is narrative prose with Canvas-based diagrams, faithful to the source textbooks.

```
Outline → RAG Query → Narrative Writing → Diagrams → Verification → Deploy
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CHEM 361 System                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Outlines   │───▶│  RAG System  │───▶│   Lectures   │       │
│  │   (.md)      │    │  (Qdrant)    │    │   (.html)    │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                   │                   │                │
│         │                   │                   ▼                │
│         │                   │           ┌──────────────┐        │
│         │                   │           │ GitHub Pages │        │
│         │                   │           │ chem361.     │        │
│         │                   │           │ thebeakers   │        │
│         │                   │           │ .com         │        │
│         │                   │           └──────────────┘        │
│         │                   │                                    │
│         ▼                   ▼                                    │
│  ┌─────────────────────────────────────────────────────┐        │
│  │                    Skills Framework                  │        │
│  │  ~/.claude/skills/chem361/                          │        │
│  │  ├── generate-lecture.md                            │        │
│  │  ├── verify-content.md                              │        │
│  │  └── create-diagrams.md                             │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Source Materials

| Component | Location | Purpose |
|-----------|----------|---------|
| Session outlines | `lectures/outlines/session_XX_outline.md` | Topic structure, learning objectives |
| Meta book | `data/meta_book.json` | Which textbook for which topic |
| Syllabus | `SYLLABUS_CHEM361.md` | Course structure, 33 sessions |

### 2. RAG System

| Setting | Value |
|---------|-------|
| Qdrant URL | `http://localhost:6333` |
| Collection | `textbooks_chunks` |
| Points | 8,756 |
| Embedding | `nomic-embed-text:latest` (768-dim) |
| Ollama URL | `http://localhost:11434` |

**Textbooks indexed:**

| PDF Name | Textbook | Best For |
|----------|----------|----------|
| `Inorganic_Chemistry_Atkins_Shriver.pdf` | Atkins & Shriver | Coordination, organometallics, theory |
| `ic_tina.pdf` | Housecroft & Sharpe | Diagrams, structure, solids |
| `ic_basset.pdf` | Basset | Classical explanations, historical |
| `descriptive_ic_house.pdf` | House | Main group, descriptive |
| `concise_ic_jd_lee.pdf` | JD Lee | Concise explanations, data |

### 3. Skills Framework

Located at `~/.claude/skills/chem361/`:

```
chem361/
├── index.md              # Quick reference
├── generate-lecture.md   # Full workflow (10KB)
├── verify-content.md     # RAG verification (5KB)
└── create-diagrams.md    # Canvas templates (9KB)
```

### 4. Output

| Output | Location | Format |
|--------|----------|--------|
| Lectures | `lectures/session_XX_*.html` | Self-contained HTML |
| Deployment | `chem361.thebeakers.com` | GitHub Pages |

---

## Workflow

### Step 1: Load Outline

```bash
cat lectures/outlines/session_01_outline.md
```

Extract:
- Topic hierarchy
- Source strategy (which textbook for what)
- Key concepts
- Required visuals

### Step 2: Query RAG

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

# example: search for lanthanide contraction
results = search("lanthanide contraction 4f shielding atomic radius", 4)
for r in results:
    print(f"[{r['payload']['pdf_name']}]")
    print(r['payload']['text'][:400])
```

**Query guidelines:**
- Use specific chemistry terms
- Include related concepts
- Search multiple formulations

### Step 3: Write Narrative

**Forbidden patterns (AI slop):**

| Pattern | Example | Why Bad |
|---------|---------|---------|
| "Not X but Y" | "Not just four trends, but..." | Cliche |
| Em-dashes | "The answer—surprisingly—is" | Overused |
| Bullet lists | "• First • Second" | Not narrative |
| "Let's explore" | "Let's explore why..." | Patronizing |
| Rhetorical Qs | "But why does this happen?" | Cheap |

**Required style:**

```html
<!-- BAD -->
<p>The lanthanide contraction is caused by:</p>
<ul>
  <li>Poor 4f shielding</li>
  <li>Increasing Zeff</li>
</ul>

<!-- GOOD -->
<p>The elements of the third transition series are preceded by the
lanthanoids, in which fourteen 4f electrons are added. These 4f
orbitals have poor shielding properties. The f electrons lie deep
within the atom and do not effectively screen outer electrons from
the nuclear charge.</p>
```

### Step 4: Create Diagrams

Use Canvas for data visualizations:

```javascript
function drawTrend(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');
    // ... plotting code

    // ALWAYS cite data source
    ctx.fillStyle = '#999';
    ctx.font = '10px monospace';
    ctx.fillText('Data: Cordero et al. 2008', 10, canvas.height - 10);
}
```

**Data sources:**

| Data Type | Source | Citation |
|-----------|--------|----------|
| Covalent radii | Cordero 2008 | Dalton Trans. 2008, 2832 |
| Ionic radii | Shannon 1976 | Acta Cryst. A32, 751 |
| Ionization energies | NIST ASD | physics.nist.gov |

### Step 5: Verify Content

Run verification queries for each major claim:

```bash
source /storage/RAG/.venv/bin/activate
python3 << 'EOF'
# ... search code ...
results = search("your claim keywords here", 4)
for r in results:
    print(f"[{r['payload']['pdf_name']}]")
    print(r['payload']['text'][:500])
EOF
```

**Checklist:**
- [ ] Zeff explanation matches Atkins
- [ ] Anomalies match Basset
- [ ] Contraction data matches Housecroft
- [ ] All numbers have citations

### Step 6: Deploy

```bash
cd /storage/inorganic-chem-class
git add lectures/session_XX_*.html
git commit -m "Add Session XX: Topic Name"
git push origin main
# GitHub Pages deploys automatically
```

---

## HTML Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Session X: Topic - CHEM 361</title>
    <style>
        :root {
            --text: #1a1a2e;
            --accent: #e94560;
            --bg: #f8f9fa;
        }

        body {
            font-family: 'Crimson Pro', Georgia, serif;
            line-height: 1.8;
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
            color: var(--text);
            background: var(--bg);
        }

        h1, h2, h3 {
            font-family: 'Space Grotesk', system-ui, sans-serif;
        }

        .equation {
            font-family: 'Times New Roman', serif;
            font-style: italic;
            text-align: center;
            margin: 1.5rem 0;
            font-size: 1.2rem;
        }

        table.data {
            border-collapse: collapse;
            margin: 1rem auto;
        }
        table.data th {
            background: var(--accent);
            color: white;
            padding: 0.5rem 1rem;
        }
        table.data td {
            border: 1px solid #ddd;
            padding: 0.5rem 1rem;
        }

        .diagram-container {
            text-align: center;
            margin: 2rem 0;
        }
        .diagram-caption {
            font-size: 0.9rem;
            color: #666;
        }

        .note {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 1rem;
            margin: 1rem 0;
        }
    </style>
</head>
<body>
    <header>
        <h1>Session X: [Topic]</h1>
        <p>CHEM 361 Inorganic Chemistry</p>
    </header>

    <main>
        <section id="section-1">
            <h2>Section Title</h2>
            <p>Narrative prose here...</p>

            <div class="diagram-container">
                <canvas id="diagram1" width="600" height="400"></canvas>
                <p class="diagram-caption">Figure 1: Description. Data from Source.</p>
            </div>
        </section>

        <!-- more sections -->
    </main>

    <footer>
        <h3>References</h3>
        <ul>
            <li>Atkins, P. & Shriver, D. <em>Inorganic Chemistry</em>. Oxford.</li>
            <li>Housecroft, C. & Sharpe, A. <em>Inorganic Chemistry</em>. Pearson.</li>
            <li>Shannon, R.D. (1976) <em>Acta Cryst.</em> A32, 751.</li>
        </ul>
    </footer>

    <script>
        // diagram code here
    </script>
</body>
</html>
```

---

## Quality Standards

### Content

- [ ] Narrative prose (no bullet points in explanations)
- [ ] No AI slop patterns
- [ ] Faithful to textbook explanations
- [ ] All data cited with sources
- [ ] Historical context where relevant
- [ ] Concepts connected to later material

### Technical

- [ ] Valid HTML5
- [ ] Mobile responsive
- [ ] Diagrams render correctly
- [ ] Interactive elements work
- [ ] Loads without external dependencies (except fonts)

### Verification

- [ ] Each major claim verified against RAG
- [ ] At least 2 textbook sources per topic
- [ ] No invented mechanisms or data
- [ ] Cross-checked numerical values

---

## Session Status

| Session | Topic | Status |
|---------|-------|--------|
| 1 | Periodic Trends | ✅ Complete |
| 2 | Coordination Geometry | ⏳ Pending |
| 3 | Crystal Field Theory | ⏳ Pending |
| ... | ... | ... |
| 33 | Review | ⏳ Pending |

---

## Troubleshooting

### Qdrant not responding

```bash
curl http://localhost:6333/collections
# if empty, start Qdrant:
docker start qdrant
```

### No relevant RAG results

- Try different query terms
- Search for specific phrases from textbooks
- Check if topic is actually in the indexed PDFs

### Diagram not rendering

- Check canvas dimensions
- Verify data array format
- Check browser console for errors

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| `DEVELOPER_SETUP.md` | Environment setup |
| `DEPLOYMENT.md` | Deploying to production |
| `API_REFERENCE.md` | API endpoints |
| `KNOWLEDGE_FUNNEL_METHODOLOGY.md` | Curriculum design theory |

---

*Framework documentation for CHEM 361 lecture generation*
