# Knowledge Funnel - Quick Start

## Run the Visualization

```bash
cd /storage/inorganic-chem-class/infrastructure
source /storage/RAG/.venv/bin/activate
python api_server.py --port 8361
```

Then open: **http://localhost:8361/funnel.html**

---

## Command Line Usage

```bash
# Trace a question
python path_tracer.py --question "Why is copper sulfate blue?"

# Trace a specific concept
python path_tracer.py --concept "Crystal Field Theory"

# Save output to file
python path_tracer.py -q "What is magnetism?" -o output.json
```

---

## Key Files

| File | Purpose |
|------|---------|
| `funnel.html` | Interactive visualization |
| `infrastructure/path_tracer.py` | Core algorithm |
| `infrastructure/api_server.py` | HTTP server |
| `infrastructure/verify_sources.py` | Data verification |
| `docs/KNOWLEDGE_FUNNEL_METHODOLOGY.md` | Full documentation |

---

## Scale Colors

- 🔴 **QUANTUM** - Orbitals, wave functions
- 🟣 **ELECTRONIC** - CFT, bonding, spectroscopy
- 🔵 **STRUCTURAL** - Symmetry, geometry
- 🟢 **DESCRIPTIVE** - Trends, properties

---

## Example Questions to Try

1. "Why is copper sulfate blue?"
2. "How does magnetism work in complexes?"
3. "What is crystal field splitting?"
4. "Why do transition metals form colored compounds?"
5. "How do point groups relate to spectroscopy?"
