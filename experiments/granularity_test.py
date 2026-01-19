#!/usr/bin/env python3
"""
Granularity Experiment: Extract at 3 levels from diverse chunks
Goal: Find the right "satellite altitude" for useful knowledge graph
"""

import json
import random
import urllib.request
from pathlib import Path
from collections import defaultdict

from qdrant_client import QdrantClient

# config
QDRANT_URL = "http://localhost:6333"
COLLECTION = "textbooks_chunks"
OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen3:latest"  # good for STEM
OUTPUT_DIR = Path("experiments/results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# experiment settings
TOTAL_SAMPLES = 500  # 5x the initial experiment
SAMPLES_PER_BOOK = 85  # ~500/6 books

client = QdrantClient(url=QDRANT_URL)


def query_llm(prompt: str, temperature: float = 0.1) -> dict:
    """query Qwen3 with JSON output"""
    # add /no_think to suppress thinking for faster response
    full_prompt = f"{prompt}\n\n/no_think"

    url = f"{OLLAMA_URL}/api/generate"
    data = json.dumps({
        "model": MODEL,
        "prompt": full_prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": temperature}
    }).encode('utf-8')

    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            return json.loads(result['response'])
    except Exception as e:
        print(f"  LLM error: {e}")
        return {}


def get_diverse_sample(n_per_book: int = SAMPLES_PER_BOOK) -> list:
    """get diverse chunks across all books and chunk positions"""
    books = {}

    # get all chunks grouped by book
    offset = None
    while True:
        results, offset = client.scroll(
            collection_name=COLLECTION,
            limit=500,
            with_payload=True,
            with_vectors=False,
            offset=offset
        )
        for point in results:
            book = point.payload.get("pdf_name", "unknown")
            if book not in books:
                books[book] = []
            books[book].append({
                "id": point.id,
                "text": point.payload.get("text", ""),
                "chunk_idx": point.payload.get("chunk_idx", 0),
                "book": book
            })
        if offset is None:
            break

    print(f"Found {len(books)} books:")
    for book, chunks in books.items():
        print(f"  {book}: {len(chunks)} chunks")

    # sample from different positions in each book (start, middle, end)
    samples = []
    for book, chunks in books.items():
        if not chunks:
            continue

        # sort by chunk_idx
        chunks.sort(key=lambda x: x["chunk_idx"])
        n = len(chunks)

        # sample from different regions
        indices = []
        if n >= n_per_book:
            # spread across the book
            step = n // n_per_book
            indices = [i * step for i in range(n_per_book)]
        else:
            indices = list(range(n))

        for idx in indices[:n_per_book]:
            samples.append(chunks[idx])

    random.shuffle(samples)
    return samples[:TOTAL_SAMPLES]  # cap at configured total


def extract_three_levels(text: str, book: str) -> dict:
    """extract topic, subtopic, and concepts from a chunk"""

    # truncate very long text
    text = text[:2000] if len(text) > 2000 else text

    prompt = f"""Analyze this inorganic chemistry textbook passage and extract knowledge at THREE levels of granularity.

PASSAGE (from {book}):
\"\"\"
{text}
\"\"\"

Extract:

1. TOPIC: The main chapter-level subject (e.g., "Crystal Field Theory", "Main Group Chemistry", "Coordination Compounds")
   - Should be broad enough to be a textbook chapter title
   - NOT specific compounds or equations

2. SUBTOPIC: The section-level subject within that topic (e.g., "Octahedral Splitting", "Spectrochemical Series", "IUPAC Nomenclature")
   - More specific than topic
   - Could be a section heading

3. KEY_CONCEPTS: 3-5 specific concepts, terms, or ideas mentioned (e.g., "CFSE", "high-spin", "d-orbital splitting")
   - The actual chemistry terms being discussed
   - NOT generic words like "energy" or "structure"

4. PREREQUISITES: What must a student already know to understand this? (1-3 items)
   - Prior knowledge assumed by this passage
   - At 300-level, skip basics like "periodic table" or "electron"

5. LEADS_TO: What topics does this enable understanding of? (1-2 items)
   - Where could a student go next?

Output as JSON:
{{
    "topic": "...",
    "subtopic": "...",
    "key_concepts": ["...", "...", "..."],
    "prerequisites": ["...", "..."],
    "leads_to": ["...", "..."],
    "confidence": 0.0-1.0
}}"""

    return query_llm(prompt)


def main():
    print("=" * 60)
    print("GRANULARITY EXPERIMENT")
    print("=" * 60)

    # get diverse sample
    print("\n[1/3] Sampling diverse chunks...")
    samples = get_diverse_sample(n_per_book=17)
    print(f"Got {len(samples)} samples")

    # extract at three levels
    print("\n[2/3] Extracting at three levels with Qwen3...")
    results = []

    for i, sample in enumerate(samples):
        print(f"  [{i+1}/{len(samples)}] {sample['book'][:30]}... chunk {sample['chunk_idx']}")

        extraction = extract_three_levels(sample["text"], sample["book"])

        if extraction:
            results.append({
                "book": sample["book"],
                "chunk_idx": sample["chunk_idx"],
                "text_preview": sample["text"][:200],
                "extraction": extraction
            })

            # show progress
            if extraction.get("topic"):
                print(f"       Topic: {extraction.get('topic', '?')}")
                print(f"       Subtopic: {extraction.get('subtopic', '?')}")

    # save results
    output_file = OUTPUT_DIR / f"granularity_experiment_{TOTAL_SAMPLES}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {len(results)} extractions to {output_file}")

    # analyze
    print("\n[3/3] Analyzing results...")
    analyze_results(results)


def analyze_results(results: list):
    """analyze the extraction results"""

    # collect unique values at each level
    topics = defaultdict(int)
    subtopics = defaultdict(int)
    concepts = defaultdict(int)
    prereqs = defaultdict(int)
    leads_to = defaultdict(int)

    for r in results:
        ext = r.get("extraction", {})

        topic = ext.get("topic", "").strip()
        if topic:
            topics[topic] += 1

        subtopic = ext.get("subtopic", "").strip()
        if subtopic:
            subtopics[subtopic] += 1

        for c in ext.get("key_concepts", []):
            if c and c.strip():
                concepts[c.strip()] += 1

        for p in ext.get("prerequisites", []):
            if p and p.strip():
                prereqs[p.strip()] += 1

        for l in ext.get("leads_to", []):
            if l and l.strip():
                leads_to[l.strip()] += 1

    print("\n" + "=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)

    print(f"\n📊 LEVEL 1 - TOPICS ({len(topics)} unique)")
    print("-" * 40)
    for topic, count in sorted(topics.items(), key=lambda x: -x[1])[:20]:
        print(f"  {count:3d}x | {topic}")

    print(f"\n📊 LEVEL 2 - SUBTOPICS ({len(subtopics)} unique)")
    print("-" * 40)
    for subtopic, count in sorted(subtopics.items(), key=lambda x: -x[1])[:25]:
        print(f"  {count:3d}x | {subtopic}")

    print(f"\n📊 LEVEL 3 - KEY CONCEPTS ({len(concepts)} unique)")
    print("-" * 40)
    for concept, count in sorted(concepts.items(), key=lambda x: -x[1])[:30]:
        print(f"  {count:3d}x | {concept}")

    print(f"\n🔗 PREREQUISITES ({len(prereqs)} unique)")
    print("-" * 40)
    for prereq, count in sorted(prereqs.items(), key=lambda x: -x[1])[:15]:
        print(f"  {count:3d}x | {prereq}")

    print(f"\n➡️  LEADS TO ({len(leads_to)} unique)")
    print("-" * 40)
    for lt, count in sorted(leads_to.items(), key=lambda x: -x[1])[:15]:
        print(f"  {count:3d}x | {lt}")

    # summary stats
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Topics:     {len(topics):4d} unique (target: 15-25)")
    print(f"  Subtopics:  {len(subtopics):4d} unique (target: 100-200)")
    print(f"  Concepts:   {len(concepts):4d} unique (target: 500-1000)")
    print(f"  Prereqs:    {len(prereqs):4d} unique")
    print(f"  Leads-to:   {len(leads_to):4d} unique")

    # save analysis
    analysis = {
        "topics": dict(topics),
        "subtopics": dict(subtopics),
        "concepts": dict(concepts),
        "prerequisites": dict(prereqs),
        "leads_to": dict(leads_to),
        "summary": {
            "n_topics": len(topics),
            "n_subtopics": len(subtopics),
            "n_concepts": len(concepts),
            "n_prereqs": len(prereqs),
            "n_leads_to": len(leads_to)
        }
    }

    analysis_file = OUTPUT_DIR / f"granularity_analysis_{TOTAL_SAMPLES}.json"
    with open(analysis_file, 'w') as f:
        json.dump(analysis, f, indent=2)

    print(f"\nAnalysis saved to {analysis_file}")


if __name__ == "__main__":
    main()
