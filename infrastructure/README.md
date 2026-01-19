# Chemistry Curriculum Infrastructure

**Robust, data-driven curriculum generation for all chemistry subfields**

---

## Directory Structure

```
infrastructure/
├── README.md                          # this file
├── verify_sources.py                  # data verification layer
├── curriculum_schema.py               # standardized schema
├── verified_manifest.json             # VERIFIED source list
└── curriculum_ic_undergraduate.json   # inorganic chemistry curriculum
```

---

## Core Principle: No Guessing

Every curriculum MUST be traceable to:
1. **Verified Qdrant collection** → `verified_manifest.json`
2. **Knowledge graph with PageRank** → `chemkg_enhanced.json`
3. **Explicit source attribution** → which textbook for which topic

---

## Adding a New Chemistry Subfield

### Step 1: Ingest Textbooks

```bash
# 1. place PDFs in RAG system
cp /path/to/organic_textbooks/*.pdf /storage/RAG/data/pdfs/

# 2. run ingestion
PDF_DIR=/storage/RAG/data/pdfs python /storage/RAG/src/ingest.py

# 3. rebuild hybrid index
python /storage/RAG/src/build_hybrid_fast.py
```

### Step 2: Verify Sources

```bash
# verify what was actually ingested
python infrastructure/verify_sources.py textbooks_chunks \
    --output infrastructure/verified_manifest_organic.json
```

**DO NOT PROCEED** if the manifest doesn't show your expected textbooks.

### Step 3: Extract Knowledge Graph

```bash
# run extraction on the new collection
python experiments/full_extraction.py --collection textbooks_chunks \
    --filter "organic" --output results/organic_extraction.json

# normalize and build graph
python experiments/normalizer.py results/organic_extraction.json \
    --output results/organic_graph.json

# compute PageRank
python experiments/curriculum_generator.py results/organic_graph.json \
    --compute-pagerank --output results/organic_enhanced.json
```

### Step 4: Generate Curriculum

Use the schema in `curriculum_schema.py`:

```python
from curriculum_schema import Curriculum, Unit, Session, Topic, Scale, Source

organic_curriculum = Curriculum(
    subfield="organic",
    course_code="CHEM 341",
    course_title="Organic Chemistry I",
    level=Level.CORE,
    credits=3,
    sources=[...],  # from verified manifest
    units=[...],    # from knowledge graph
    source_manifest="verified_manifest_organic.json",
    knowledge_graph="organic_enhanced.json"
)
```

### Step 5: Validate

```python
from curriculum_schema import validate_curriculum

errors = validate_curriculum(organic_curriculum)
if errors:
    print("VALIDATION FAILED:")
    for e in errors:
        print(f"  - {e}")
else:
    organic_curriculum.to_json("curriculum_organic.json")
```

---

## Verification Checklist

Before trusting any curriculum:

- [ ] `verify_sources.py` shows expected textbooks
- [ ] Chunk counts match expectations
- [ ] Knowledge graph has PageRank computed
- [ ] Source attribution is explicit for every topic
- [ ] No "unknown" or "MISSING" sources

---

## Source Registry

Update `curriculum_schema.py` when adding new subfields:

```python
SOURCE_REGISTRY = {
    "inorganic": {
        "Atkins": "Inorganic_Chemistry_Atkins_Shriver.pdf",
        # ...
    },
    "organic": {
        "Clayden": "organic_chemistry_clayden.pdf",
        "Wade": "organic_chemistry_wade.pdf",
        # ...
    },
    "physical": {
        "Atkins": "physical_chemistry_atkins.pdf",
        # ...
    },
    # etc.
}
```

---

## Inorganic Chemistry Status

**VERIFIED** as of 2026-01-18:

| Source | PDF | Chunks | Status |
|--------|-----|--------|--------|
| Atkins | Inorganic_Chemistry_Atkins_Shriver.pdf | 2,494 | ✓ |
| Housecroft | ic_tina.pdf | 2,375 | ✓ |
| Douglas | descriptive_ic.pdf | 1,495 | ✓ |
| House | descriptive_ic_house.pdf | 1,027 | ✓ |
| JD Lee | concise_ic_jd_lee.pdf | 565 | ✓ |
| Basset | ic_basset.pdf | 446 | ✓ |
| Advanced | advancex_ic_applicaionts.pdf | 351 | ✓ |

**Total: 8,753 chunks from 7 IC textbooks**

---

## Knowledge Graph Stats

From `chemkg_enhanced.json`:
- **Nodes:** 5,380
- **Edges:** 2,885
- **Significant topics (count≥10):** 67
- **PageRank computed:** Yes

---

## Curriculum Generated

`curriculum_ic_undergraduate.json`:
- **Units:** 6
- **Sessions:** 33
- **Scale distribution:** QUANTUM(1), DESCRIPTIVE(11), STRUCTURAL(13), ELECTRONIC(8)

---

## Future Subfields

| Subfield | Status | Next Step |
|----------|--------|-----------|
| Inorganic | ✓ COMPLETE | Generate quizzes |
| Organic | NOT STARTED | Ingest textbooks |
| Physical | NOT STARTED | Ingest textbooks |
| Analytical | NOT STARTED | Ingest textbooks |
| Biological | NOT STARTED | Ingest textbooks |
| Materials | NOT STARTED | Ingest textbooks |

---

## Troubleshooting

### "Source not in manifest"
The PDF wasn't ingested or has a different name. Check:
```bash
ls /storage/RAG/data/pdfs/ | grep -i <expected_name>
```

### "PageRank is 0 for all topics"
Run the enhancement step:
```bash
python experiments/curriculum_generator.py graph.json --compute-pagerank
```

### "Collection not found"
Qdrant may not be running:
```bash
curl http://localhost:6333/collections
```

---

*Infrastructure designed for reliability across all chemistry subfields.*
