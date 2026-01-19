# Developer Setup Guide

**CHEM 361 Inorganic Chemistry - Knowledge Funnel System**

---

## Prerequisites

Before setting up the project, ensure you have:

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.10+ | Backend scripts |
| Node.js | 18+ | (Optional) Frontend tooling |
| Ollama | Latest | LLM and embeddings |
| Qdrant | 1.7+ | Vector database |
| Git | 2.x | Version control |

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/khatvangi/inorganic-chem-class.git
cd inorganic-chem-class

# 2. Set up Python environment
source /storage/RAG/.venv/bin/activate  # Use existing RAG venv
# OR create new:
# python -m venv .venv && source .venv/bin/activate
# pip install qdrant-client networkx

# 3. Start required services
# Qdrant should be running on port 6333
# Ollama should be running on port 11434

# 4. Start the API server
cd infrastructure
python api_server.py --port 8361

# 5. Open browser
# http://localhost:8361/visualizations/
```

---

## Project Structure

```
inorganic-chem-class/
│
├── infrastructure/           # Backend Python code
│   ├── api_server.py         # HTTP server (port 8361)
│   ├── path_tracer.py        # Prerequisite tracing algorithm
│   ├── lecture_qa_generator.py  # Content generation
│   ├── curriculum_schema.py  # Data structures
│   └── verify_sources.py     # Data verification
│
├── visualizations/           # Interactive D3.js views
│   ├── index.html            # Landing page
│   ├── scales.html           # Scale-layered graph
│   └── hierarchy.html        # Radial/tree view
│
├── lectures/                 # Lecture content
│   ├── session_01_periodic_trends.html  # Interactive lecture
│   └── generated/            # Auto-generated lectures
│
├── data/                     # JSON data files
│   ├── meta_book.json        # Session → textbook mapping
│   ├── quizzes/              # Quiz question banks
│   └── topic_flow.json       # Topic sequencing
│
├── experiments/              # Knowledge extraction scripts
│   ├── full_extraction.py    # Extract from Qdrant
│   ├── normalizer.py         # Normalize concept names
│   └── results/              # Extraction outputs
│       └── knowledge_graph.json
│
├── docs/                     # Documentation
│   ├── API_REFERENCE.md
│   ├── DEVELOPER_SETUP.md    # This file
│   ├── DEPLOYMENT.md
│   └── KNOWLEDGE_FUNNEL_METHODOLOGY.md
│
├── libs/                     # External libraries
│   ├── ChemDoodleWeb.js      # Molecule visualization
│   └── ChemDoodleWeb.css
│
├── js/                       # Shared JavaScript
│   └── utils.js              # Common utilities
│
├── funnel.html               # Main funnel visualization
├── SYLLABUS_CHEM361.md       # Course syllabus
└── README.md                 # Project overview
```

---

## Service Dependencies

### 1. Qdrant Vector Database

**Check if running:**
```bash
curl http://localhost:6333/collections
```

**Expected collections:**
| Collection | Points | Description |
|------------|--------|-------------|
| `textbooks_chunks` | 8,753 | Textbook content with embeddings |

**Start Qdrant (if not running):**
```bash
# Using Docker
docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant

# Or using local binary
./qdrant --config-path config.yaml
```

### 2. Ollama LLM Server

**Check if running:**
```bash
curl http://localhost:11434/api/tags
```

**Required models:**
| Model | Purpose |
|-------|---------|
| `nomic-embed-text:latest` | Text embeddings (768-dim) |
| `qwen3:latest` | Content generation |

**Install models:**
```bash
ollama pull nomic-embed-text:latest
ollama pull qwen3:latest
```

**Start Ollama:**
```bash
ollama serve
```

---

## Environment Variables

Create a `.env` file or export these variables:

```bash
# Qdrant
export QDRANT_URL="http://localhost:6333"
export COLLECTION="textbooks_chunks"

# Ollama
export OLLAMA_URL="http://localhost:11434"
export OLLAMA_MODEL="qwen3:latest"
export EMBED_MODEL="nomic-embed-text:latest"

# Server
export API_PORT=8361
```

---

## Development Workflow

### Running the API Server

```bash
cd infrastructure
source /storage/RAG/.venv/bin/activate
python api_server.py --port 8361
```

The server provides:
- API endpoints at `/api/*`
- Static file serving for visualizations
- CORS enabled for development

### Testing the API

```bash
# Health check
curl http://localhost:8361/api/health

# Trace prerequisites
curl "http://localhost:8361/api/trace?q=crystal+field+theory"

# List concepts
curl http://localhost:8361/api/concepts
```

### Generating Lectures

```bash
cd infrastructure
source /storage/RAG/.venv/bin/activate

# Generate for one session
python lecture_qa_generator.py --session 1

# Generate for a unit
python lecture_qa_generator.py --unit 1

# Generate all
python lecture_qa_generator.py --all
```

### Modifying Visualizations

The D3.js visualizations are in `/visualizations/`. To modify:

1. Edit the HTML file directly
2. Refresh browser (no build step required)
3. Test with different queries using `?q=` parameter

```bash
# Test scales view with a query
open "http://localhost:8361/visualizations/scales.html?q=magnetism"
```

---

## Data Pipeline

### 1. Textbook Ingestion (Already Done)

```bash
# Add PDFs to RAG system
cp new_textbook.pdf /storage/RAG/data/pdfs/

# Run ingestion
cd /storage/RAG
source .venv/bin/activate
PDF_DIR=/storage/RAG/data/pdfs python src/ingest.py

# Rebuild hybrid index
python src/build_hybrid_fast.py
```

### 2. Knowledge Extraction

```bash
cd experiments
source /storage/RAG/.venv/bin/activate

# Extract from all chunks
python full_extraction.py --collection textbooks_chunks

# Normalize concepts
python normalizer.py results/full_extraction_results.json

# Output: results/knowledge_graph.json
```

### 3. Verify Sources

```bash
cd infrastructure
python verify_sources.py textbooks_chunks
# Output: verified_manifest.json
```

---

## Key Files Explained

### `infrastructure/path_tracer.py`

Core algorithm for tracing prerequisites:

```python
class PathTracer:
    def trace_prerequisites(self, target: str, max_depth: int = 5) -> dict:
        """
        BFS traversal backward through prerequisite edges.
        Returns nodes, edges, and layer distribution by scale.
        """

    def _infer_scale(self, topic_name: str) -> str:
        """
        Classify concept into QUANTUM/ELECTRONIC/STRUCTURAL/DESCRIPTIVE
        based on keyword matching.
        """
```

### `infrastructure/api_server.py`

HTTP server using Python's built-in `http.server`:

```python
# Endpoints:
# GET /api/trace?q=<question>  → trace prerequisites
# GET /api/concepts            → list all concepts
# GET /api/health              → server status
# GET /*                       → static files
```

### `infrastructure/lecture_qa_generator.py`

Content generation pipeline:

```python
class LectureQAGenerator:
    def generate_lecture(self, session_num: int) -> str:
        # 1. Load session from meta_book.json
        # 2. Query Qdrant for relevant chunks
        # 3. Call LLM to synthesize lecture
        # 4. Save to lectures/generated/

    def generate_qa(self, session_num: int) -> list:
        # 1. Load session info
        # 2. Query Qdrant for content
        # 3. Generate questions at 3 difficulty levels
        # 4. Save to data/quizzes/generated/
```

### `data/meta_book.json`

Maps sessions to textbook sources:

```json
{
  "unit_1_main_group": {
    "primary_source": "house",
    "sessions": [
      {
        "session": 1,
        "topic": "Periodic trends",
        "sources": {
          "theory": "lee",
          "examples": "house",
          "visuals": "housecroft"
        },
        "key_concepts": ["atomic radius", "ionization energy"]
      }
    ]
  }
}
```

---

## Testing

### Manual Testing

```bash
# Test embedding function
python -c "
from lecture_qa_generator import embed_query
vec = embed_query('atomic radius')
print(f'Embedding dim: {len(vec)}')
"

# Test Qdrant query
python -c "
from lecture_qa_generator import LectureQAGenerator
gen = LectureQAGenerator()
chunks = gen._query_qdrant(['crystal field'], ['atkins'], limit=3)
print(f'Found {len(chunks)} chunks')
"

# Test path tracer
python -c "
from path_tracer import PathTracer
pt = PathTracer()
result = pt.trace_prerequisites('Crystal Field Theory')
print(f'Nodes: {len(result[\"all_nodes\"])}')
print(f'Layers: {list(result[\"layers\"].keys())}')
"
```

### Browser Testing

1. Open http://localhost:8361/visualizations/
2. Try example queries
3. Click nodes to re-trace
4. Check console for errors

---

## Common Issues

### "Qdrant connection refused"

```bash
# Check if Qdrant is running
curl http://localhost:6333/collections

# Start Qdrant
docker start qdrant  # if using Docker
```

### "Ollama model not found"

```bash
# List available models
ollama list

# Pull required model
ollama pull nomic-embed-text:latest
ollama pull qwen3:latest
```

### "No chunks retrieved"

Check the PDF name mapping in `lecture_qa_generator.py`:

```python
SOURCE_PDF_MAP = {
    "atkins": "Inorganic_Chemistry_Atkins_Shriver.pdf",
    "lee": "concise_ic_jd_lee.pdf",
    # ... etc
}
```

### "Knowledge graph not found"

```bash
# Regenerate if needed
cd experiments
python full_extraction.py --collection textbooks_chunks
python normalizer.py results/full_extraction_results.json
```

---

## Contributing

### Code Style

- Python: Follow PEP 8
- JavaScript: ES6+ modules
- Comments: Lowercase, explain "why" not "what"

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-visualization

# Make changes
# ...

# Commit with descriptive message
git commit -m "Add radial tree layout option to hierarchy view"

# Push and create PR
git push -u origin feature/new-visualization
```

### Adding New Visualizations

1. Copy existing HTML template (e.g., `scales.html`)
2. Modify D3.js layout/forces
3. Add link to `visualizations/index.html`
4. Update documentation

---

## Resources

| Resource | Location |
|----------|----------|
| D3.js docs | https://d3js.org |
| ChemDoodle docs | https://web.chemdoodle.com/docs |
| Qdrant docs | https://qdrant.tech/documentation |
| Ollama docs | https://ollama.ai/docs |

---

*Developer setup guide for CHEM 361 Knowledge Funnel System*
