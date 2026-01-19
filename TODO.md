# CHEM 361 - Project TODO

**Last Updated:** January 18, 2026, 12:45 PM
**Session:** Knowledge Graph + Attendance System Build

---

## In Progress

### Knowledge Extraction (Running in Background)
- **Script:** `experiments/full_extraction.py`
- **Status:** ~1,800/7,726 chunks (23%)
- **ETA:** ~16:18 (4 hours from start)
- **Output:** `experiments/results/knowledge_graph.json`

**To check progress:**
```bash
tail -20 /storage/inorganic-chem-class/experiments/results/full_extraction.log
```

---

## Pending Tasks (After Extraction Completes)

### 1. Build Final Knowledge Graph
When extraction finishes, the graph auto-builds. Verify with:
```bash
cat experiments/results/knowledge_graph.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Nodes: {len(d[\"nodes\"])}, Edges: {len(d[\"edges\"])}')"
```

### 2. Run Textbook Style Analysis
Analyze each book's pedagogy, strengths, presentation style:
```bash
cd /storage/inorganic-chem-class
source /storage/RAG/.venv/bin/activate
python experiments/analyze_textbooks.py
```
**Output:** `experiments/results/textbook_analysis.json`

### 3. Extract House Textbook Chunks
The new `descriptive_ic_house.pdf` was added to Qdrant (1,027 chunks) but needs knowledge extraction:
```bash
# create script for just House chunks, or re-run full extraction
```

### 4. Integrate Knowledge Graph with Topic Explorer
- Update `topics.js` to load from `experiments/results/knowledge_graph.json`
- Currently uses fallback data
- Path: `./experiments/results/knowledge_graph.json`

### 5. Add Narrative Content to Topics
- Use RAG to fetch relevant chunks for each topic
- Display synthesized content from multiple textbooks
- Preserve each book's unique voice

---

## Completed (This Session)

### Attendance System
- [x] `attendance.html` - Student/instructor interface
- [x] `attendance.js` - QR codes, check-in, CSV export
- [x] `data/schedule.json` - 30 class sessions from syllabus
- [x] Instructor password: `chem361`
- [x] 15-minute code expiry with timer

### Topic Explorer
- [x] `topics.html` - D3.js force-directed graph
- [x] `topics.js` - Interactive visualization
- [x] Sidebar with search
- [x] Prerequisite/leads-to relationships
- [x] Fallback topic data (until extraction completes)

### Knowledge Graph Pipeline
- [x] `experiments/normalizer.py` - Canonical names, filtering
- [x] `experiments/full_extraction.py` - Full pipeline
- [x] `experiments/analyze_textbooks.py` - Style analysis (ready to run)
- [x] Tested on 500 chunks - normalization working

### Textbook Ingestion
- [x] Added `descriptive_ic_house.pdf` to `/storage/textbooks/`
- [x] Ingested 1,027 chunks into `textbooks_chunks`
- [x] Total: 8,756 chunks from 7 textbooks

### Documentation
- [x] Updated `ONBOARDING.md` with new features
- [x] Created `TODO.md` (this file)

---

## Textbooks in Qdrant

| Textbook | Chunks | Notes |
|----------|--------|-------|
| Atkins/Shriver | 2,494 | Comprehensive, authoritative |
| ic_tina.pdf | 2,375 | Detailed coverage |
| descriptive_ic.pdf | 1,495 | Narrative style |
| descriptive_ic_house.pdf | 1,027 | NEW - highlight boxes, clear presentation |
| JD Lee (concise) | 565 | Foundational |
| ic_basset.pdf | 446 | Applications focus |
| advanced_ic_applications | 351 | Advanced topics |

---

## Future Enhancements

### Short-term
- [ ] ChemDoodle: Load real MOL/SDF files for complex molecules
- [ ] Attendance: Backend API for persistent storage
- [ ] Topics: Add textbook-specific narrative sections

### Medium-term
- [ ] Multi-LLM validation (Mistral already pulled)
- [ ] Topic-wise quiz generation from knowledge graph
- [ ] Student progress tracking across topics

### Long-term
- [ ] Extend to pchem, organic, analytical layers
- [ ] Cross-course knowledge graph
- [ ] Personalized learning paths based on prerequisites

---

## Quick Commands

```bash
# activate environment
source /storage/RAG/.venv/bin/activate

# check extraction progress
tail -20 experiments/results/full_extraction.log

# run textbook analysis (after extraction)
python experiments/analyze_textbooks.py

# test site locally
python3 -m http.server 8080

# query Qdrant
python /storage/RAG/src/query.py "crystal field theory"
```

---

## Contact

**Instructor:** Kiran Boggavarapu
**Course:** CHEM 361 - Inorganic Chemistry, Spring 2025
**Site:** https://chem361.thebeakers.com
