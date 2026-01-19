# Extraction Parameters & Prompts

**Purpose:** Document all parameters for reproducibility.
**Last Updated:** 2026-01-18

---

## 1. Data Ingestion Parameters

### PDF Chunking
```yaml
chunk_size: 2000  # characters
chunk_overlap: 200  # characters
min_chunk_length: 100  # characters
```

### Embedding
```yaml
model: nomic-embed-text:latest
dimensions: 768
backend: ollama
url: http://localhost:11434
```

### Vector Database
```yaml
engine: qdrant
url: http://localhost:6333
collection: textbooks_chunks
distance_metric: cosine
```

---

## 2. Knowledge Extraction Parameters

### LLM Configuration
```yaml
model: qwen3:latest
temperature: 0.1
num_ctx: 4096
timeout: 120  # seconds
backend: ollama
```

### Extraction Prompt (v1.0)
```
Analyze this inorganic chemistry textbook passage and extract knowledge at THREE levels of granularity.

PASSAGE:
"""
{text[:2500]}
"""

Extract:
1. TOPIC: The main chapter-level subject (e.g., "Coordination Chemistry", "Crystal Field Theory")
2. SUBTOPIC: The section-level subject within that topic
3. KEY_CONCEPTS: 3-5 specific concepts, terms, or ideas mentioned
4. PREREQUISITES: What must a student already know to understand this?
5. LEADS_TO: What topics does this enable understanding of?

Return JSON:
{
    "topic": "main topic name",
    "subtopic": "section-level topic",
    "concepts": ["concept1", "concept2", "concept3"],
    "prerequisites": ["prereq1", "prereq2"],
    "leads_to": ["topic1", "topic2"]
}

Return ONLY valid JSON, no explanations.

/no_think
```

### Processing Parameters
```yaml
batch_size: 1  # sequential for consistency
save_interval: 50  # chunks between saves
max_retries: 3
retry_delay: 2  # seconds
```

---

## 3. Normalization Rules

### Topic Mappings (excerpt)
```python
TOPIC_MAPPINGS = {
    # coordination chemistry variants
    "coordination compounds": "Coordination Chemistry",
    "coordination chemistry": "Coordination Chemistry",
    "metal complexes": "Coordination Chemistry",

    # solid state variants
    "solid state chemistry": "Solid State Chemistry",
    "solid-state chemistry": "Solid State Chemistry",
    "crystal chemistry": "Solid State Chemistry",

    # bonding variants
    "chemical bonding": "Chemical Bonding",
    "covalent bonding": "Chemical Bonding",
    "ionic bonding": "Chemical Bonding",

    # periodic table variants
    "periodic trends": "Periodic Trends",
    "periodic properties": "Periodic Trends",
    "periodicity": "Periodic Trends",

    # ... 50+ additional mappings
}
```

### Garbage Topics (filtered out)
```python
GARBAGE_TOPICS = {
    "inorganic chemistry",
    "textbook introduction",
    "general chemistry",
    "chapter summary",
    "review questions",
    "further reading",
    "bibliography",
    "index",
    "preface",
    "acknowledgments",
}
```

### Normalization Algorithm
```python
def normalize_topic(topic: str) -> str | None:
    if not topic:
        return None

    # lowercase for matching
    topic_lower = topic.lower().strip()

    # check garbage
    if topic_lower in GARBAGE_TOPICS:
        return None

    # check mappings
    if topic_lower in TOPIC_MAPPINGS:
        return TOPIC_MAPPINGS[topic_lower]

    # title case if no mapping
    return topic.title()
```

---

## 4. Graph Construction Parameters

### Node Filtering
```yaml
min_topic_count: 1  # include all topics
min_concept_count: 1  # include all concepts
```

### Edge Weights
```yaml
contains_weight: count of co-occurrences
prerequisite_weight: count of mentions
leads_to_weight: count of mentions
```

### Visualization Filtering
```yaml
max_nodes_in_graph: 150  # for D3.js performance
min_count_for_display: 10  # topic mentions threshold
```

---

## 5. Textbook Analysis Parameters (Planned)

### Analysis Prompt Template
```
Analyze the {DIMENSION} of this inorganic chemistry textbook based on these sample passages.

TEXTBOOK: {book_name}

SAMPLE PASSAGES:
"""
{combined_samples}
"""

Provide a JSON response with:
{dimension_specific_schema}

Return ONLY valid JSON.
```

### Dimensions
1. Pedagogy: teaching philosophy, difficulty, prerequisites
2. Presentation Style: tone, complexity, analogies
3. Strengths/Weaknesses: coverage, clarity, depth
4. Visual Elements: diagram density, integration

### Sampling Strategy
```yaml
samples_per_book: 25
stratified: true  # early, middle, late sections
sample_length: 1500  # characters per sample
```

---

## 6. Validation Parameters (Planned)

### Multi-LLM Consensus
```yaml
primary_model: qwen3:latest
validation_model: mistral:7b-instruct-v0.3-q4_K_M
consensus_threshold: 0.8  # agreement rate
```

### Quality Metrics
```yaml
valid_json_rate: target > 0.95
non_garbage_rate: target > 0.80
topic_consistency: target > 0.85  # same text → same topic
```

---

## 7. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-18 | Initial parameters documented |

---

*Parameters subject to tuning based on validation results.*
