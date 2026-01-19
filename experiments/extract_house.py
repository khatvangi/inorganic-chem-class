#!/usr/bin/env python3
"""
Extract knowledge from House textbook (descriptive_ic_house.pdf)
Runs same pipeline as full_extraction.py but only on House chunks.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from qdrant_client import QdrantClient
import urllib.request

# config
QDRANT_URL = "http://localhost:6333"
COLLECTION = "textbooks_chunks"
OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen3:latest"
OUTPUT_DIR = Path("experiments/results")

# import normalizer
sys.path.insert(0, str(Path(__file__).parent))
from normalizer import normalize_extraction

client = QdrantClient(url=QDRANT_URL)


def query_llm(prompt: str) -> str:
    """query Qwen3 for extraction"""
    full_prompt = f"{prompt}\n\n/no_think"

    url = f"{OLLAMA_URL}/api/generate"
    data = json.dumps({
        "model": MODEL,
        "prompt": full_prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_ctx": 4096}
    }).encode('utf-8')

    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('response', '')
    except Exception as e:
        return f"[ERROR: {e}]"


def get_house_chunks():
    """get all chunks from House textbook"""
    results, _ = client.scroll(
        collection_name=COLLECTION,
        scroll_filter={
            "must": [
                {"key": "pdf_name", "match": {"value": "descriptive_ic_house.pdf"}}
            ]
        },
        limit=2000,
        with_payload=True,
        with_vectors=False
    )
    return results


def extract_from_chunk(text: str, chunk_idx: int) -> dict:
    """extract topics, concepts, prerequisites from a chunk"""

    prompt = f"""Analyze this inorganic chemistry textbook passage and extract knowledge at THREE levels of granularity.

PASSAGE:
\"\"\"
{text[:2500]}
\"\"\"

Extract:
1. TOPIC: The main chapter-level subject (e.g., "Coordination Chemistry", "Crystal Field Theory")
2. SUBTOPIC: The section-level subject within that topic
3. KEY_CONCEPTS: 3-5 specific concepts, terms, or ideas mentioned
4. PREREQUISITES: What must a student already know to understand this?
5. LEADS_TO: What topics does this enable understanding of?

Return JSON:
{{
    "topic": "main topic name",
    "subtopic": "section-level topic",
    "concepts": ["concept1", "concept2", "concept3"],
    "prerequisites": ["prereq1", "prereq2"],
    "leads_to": ["topic1", "topic2"]
}}

Return ONLY valid JSON, no explanations."""

    response = query_llm(prompt)

    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except:
        pass

    return None


def main():
    print("=" * 60)
    print("HOUSE TEXTBOOK EXTRACTION")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # get House chunks
    chunks = get_house_chunks()
    print(f"Found {len(chunks)} chunks from descriptive_ic_house.pdf")
    print()

    results = []
    topics_count = defaultdict(int)
    concepts_set = set()

    for i, chunk in enumerate(chunks):
        text = chunk.payload.get('text', '')
        chunk_idx = chunk.payload.get('chunk_idx', i)

        extraction = extract_from_chunk(text, chunk_idx)

        if extraction and extraction.get('topic'):
            # normalize
            normalized = normalize_extraction(extraction)

            if normalized.get('topic'):
                results.append({
                    'chunk_id': chunk.id,
                    'chunk_idx': chunk_idx,
                    'extraction': normalized
                })

                topics_count[normalized['topic']] += 1
                for c in normalized.get('concepts', []):
                    concepts_set.add(c)

                print(f"[{i+1}/{len(chunks)}] chunk {chunk_idx} → {normalized['topic']}")
            else:
                print(f"[{i+1}/{len(chunks)}] chunk {chunk_idx} → (filtered)")
        else:
            print(f"[{i+1}/{len(chunks)}] chunk {chunk_idx} → (no extraction)")

        # save progress every 100
        if (i + 1) % 100 == 0:
            print(f"  [Progress saved: {len(results)} results]")
            with open(OUTPUT_DIR / "house_extraction_progress.json", 'w') as f:
                json.dump(results, f)

    # save final results
    output = {
        'book': 'descriptive_ic_house.pdf',
        'total_chunks': len(chunks),
        'extracted': len(results),
        'topics': dict(topics_count),
        'concepts': list(concepts_set),
        'results': results,
        'timestamp': datetime.now().isoformat()
    }

    with open(OUTPUT_DIR / "house_extraction.json", 'w') as f:
        json.dump(output, f, indent=2)

    print()
    print("=" * 60)
    print("HOUSE EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"Chunks processed: {len(chunks)}")
    print(f"Extractions: {len(results)}")
    print(f"Unique topics: {len(topics_count)}")
    print(f"Unique concepts: {len(concepts_set)}")
    print()
    print("Top 10 topics:")
    for topic, count in sorted(topics_count.items(), key=lambda x: -x[1])[:10]:
        print(f"  {count:4d} | {topic}")
    print()
    print(f"Saved to: {OUTPUT_DIR / 'house_extraction.json'}")


if __name__ == "__main__":
    main()
