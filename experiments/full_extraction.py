#!/usr/bin/env python3
"""
Full knowledge extraction from all textbook chunks.
Applies normalization and saves progress incrementally.

Estimated time: ~2-3 hours for 7,700 chunks
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime, timedelta

from qdrant_client import QdrantClient
import urllib.request

# import normalizer from same directory
from normalizer import normalize_extraction, analyze_normalization, print_analysis

# config
QDRANT_URL = "http://localhost:6333"
COLLECTION = "textbooks_chunks"
OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen3:latest"
OUTPUT_DIR = Path("experiments/results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# output files
PROGRESS_FILE = OUTPUT_DIR / "full_extraction_progress.json"
RESULTS_FILE = OUTPUT_DIR / "full_extraction_results.json"
GRAPH_FILE = OUTPUT_DIR / "knowledge_graph.json"

# save progress every N chunks
SAVE_INTERVAL = 50

client = QdrantClient(url=QDRANT_URL)


def query_llm(prompt: str, temperature: float = 0.1) -> dict:
    """query Qwen3 with JSON output"""
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
        return {"error": str(e)}


def get_all_chunks():
    """get all chunks from Qdrant"""
    all_chunks = []
    offset = None

    print("Loading all chunks from Qdrant...")
    while True:
        results, offset = client.scroll(
            collection_name=COLLECTION,
            limit=500,
            with_payload=True,
            with_vectors=False,
            offset=offset
        )

        for point in results:
            all_chunks.append({
                "id": point.id,
                "text": point.payload.get("text", ""),
                "chunk_idx": point.payload.get("chunk_idx", 0),
                "book": point.payload.get("pdf_name", "unknown"),
                "doc_id": point.payload.get("doc_id", "")
            })

        print(f"  Loaded {len(all_chunks)} chunks...", end='\r')

        if offset is None:
            break

    print(f"\nTotal: {len(all_chunks)} chunks from Qdrant")
    return all_chunks


def extract_knowledge(text: str, book: str) -> dict:
    """extract topic, subtopic, concepts from a chunk"""
    text = text[:2000] if len(text) > 2000 else text

    prompt = f"""Analyze this inorganic chemistry textbook passage and extract knowledge at THREE levels.

PASSAGE (from {book}):
\"\"\"
{text}
\"\"\"

Extract:
1. TOPIC: Main chapter-level subject (e.g., "Crystal Field Theory", "Main Group Chemistry")
2. SUBTOPIC: Section-level subject (e.g., "Octahedral Splitting", "Spectrochemical Series")
3. KEY_CONCEPTS: 3-5 specific chemistry terms (e.g., "CFSE", "high-spin", "d-orbital splitting")
4. PREREQUISITES: What must a student know first? (1-3 items, skip basics like "periodic table")
5. LEADS_TO: What topics does this enable? (1-2 items)

Output JSON:
{{
    "topic": "...",
    "subtopic": "...",
    "key_concepts": ["...", "..."],
    "prerequisites": ["...", "..."],
    "leads_to": ["...", "..."],
    "confidence": 0.0-1.0
}}"""

    return query_llm(prompt)


def load_progress():
    """load existing progress if any"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"processed_ids": [], "results": []}


def save_progress(progress):
    """save progress to file"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)


def main():
    print("=" * 60)
    print("FULL KNOWLEDGE EXTRACTION")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # load all chunks
    all_chunks = get_all_chunks()
    total = len(all_chunks)

    # load existing progress
    progress = load_progress()
    processed_ids = set(progress["processed_ids"])
    results = progress["results"]

    # filter out already processed
    remaining = [c for c in all_chunks if c["id"] not in processed_ids]
    print(f"Already processed: {len(processed_ids)}")
    print(f"Remaining: {len(remaining)}")

    if not remaining:
        print("All chunks already processed!")
        # skip to analysis
        analyze_and_build_graph(results)
        return

    # estimate time
    avg_time = 3.5  # seconds per chunk
    est_hours = (len(remaining) * avg_time) / 3600
    print(f"Estimated time: {est_hours:.1f} hours")
    print()

    # process chunks
    start_time = time.time()
    errors = 0

    for i, chunk in enumerate(remaining):
        # progress display
        elapsed = time.time() - start_time
        if i > 0:
            rate = i / elapsed
            remaining_time = (len(remaining) - i) / rate
            eta = datetime.now() + timedelta(seconds=remaining_time)
            eta_str = eta.strftime('%H:%M')
        else:
            eta_str = "calculating..."

        print(f"[{len(results)+1}/{total}] {chunk['book'][:25]}... chunk {chunk['chunk_idx']:4d} | ETA: {eta_str}", end='')
        sys.stdout.flush()

        # skip very short chunks
        if len(chunk["text"]) < 100:
            print(" (skipped - too short)")
            processed_ids.add(chunk["id"])
            continue

        # extract
        extraction = extract_knowledge(chunk["text"], chunk["book"])

        if "error" in extraction:
            print(f" ERROR: {extraction['error'][:30]}")
            errors += 1
            if errors > 50:
                print("\nToo many errors, stopping.")
                break
            continue

        # normalize
        normalized = normalize_extraction(extraction)

        # store result
        result = {
            "chunk_id": chunk["id"],
            "book": chunk["book"],
            "chunk_idx": chunk["chunk_idx"],
            "extraction_raw": extraction,
            "extraction_normalized": normalized
        }
        results.append(result)
        processed_ids.add(chunk["id"])

        # show topic
        topic = normalized.get("topic", "?")
        print(f" → {topic[:30] if topic else '(filtered)'}")

        # save progress periodically
        if (i + 1) % SAVE_INTERVAL == 0:
            progress = {
                "processed_ids": list(processed_ids),
                "results": results,
                "last_saved": datetime.now().isoformat()
            }
            save_progress(progress)
            print(f"  [Progress saved: {len(results)} results]")

    # final save
    progress = {
        "processed_ids": list(processed_ids),
        "results": results,
        "completed": datetime.now().isoformat()
    }
    save_progress(progress)

    print(f"\n{'=' * 60}")
    print(f"Extraction complete!")
    print(f"Total processed: {len(results)}")
    print(f"Errors: {errors}")
    print(f"Time: {(time.time() - start_time) / 60:.1f} minutes")

    # analyze and build graph
    analyze_and_build_graph(results)


def analyze_and_build_graph(results):
    """analyze results and build knowledge graph"""
    print(f"\n{'=' * 60}")
    print("BUILDING KNOWLEDGE GRAPH")
    print("=" * 60)

    # extract normalized data for analysis
    extractions = [{"extraction": r["extraction_normalized"]} for r in results]
    analysis = analyze_normalization(extractions)
    print_analysis(analysis)

    # build graph structure
    nodes = {}
    edges = []

    # add topic nodes
    for topic, count in analysis["topics"].items():
        if topic:
            nodes[topic] = {
                "id": topic,
                "label": topic,
                "type": "topic",
                "count": count,
                "group": "topic"
            }

    # add concept nodes (top 200 by frequency)
    top_concepts = sorted(analysis["concepts"].items(), key=lambda x: -x[1])[:200]
    for concept, count in top_concepts:
        if concept and concept not in nodes:
            nodes[concept] = {
                "id": concept,
                "label": concept,
                "type": "concept",
                "count": count,
                "group": "concept"
            }

    # add prerequisite nodes
    for prereq, count in analysis["prerequisites"].items():
        if prereq and prereq not in nodes:
            nodes[prereq] = {
                "id": prereq,
                "label": prereq,
                "type": "prerequisite",
                "count": count,
                "group": "prerequisite"
            }

    # build edges from results
    edge_counts = {}

    for r in results:
        norm = r["extraction_normalized"]
        topic = norm.get("topic")
        if not topic:
            continue

        # topic → concepts
        for concept in norm.get("key_concepts", []):
            if concept in nodes:
                key = (topic, concept, "contains")
                edge_counts[key] = edge_counts.get(key, 0) + 1

        # prerequisites → topic
        for prereq in norm.get("prerequisites", []):
            if prereq in nodes:
                key = (prereq, topic, "prerequisite_for")
                edge_counts[key] = edge_counts.get(key, 0) + 1

        # topic → leads_to
        for dest in norm.get("leads_to", []):
            if dest in nodes:
                key = (topic, dest, "leads_to")
                edge_counts[key] = edge_counts.get(key, 0) + 1

    # create edges with weights
    for (source, target, relation), count in edge_counts.items():
        if count >= 2:  # filter noise - require at least 2 occurrences
            edges.append({
                "source": source,
                "target": target,
                "relation": relation,
                "weight": count
            })

    # build final graph
    graph = {
        "nodes": list(nodes.values()),
        "edges": edges,
        "metadata": {
            "total_chunks": len(results),
            "unique_topics": len(analysis["topics"]),
            "unique_concepts": len(analysis["concepts"]),
            "unique_prereqs": len(analysis["prerequisites"]),
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "generated": datetime.now().isoformat()
        }
    }

    # save graph
    with open(GRAPH_FILE, 'w') as f:
        json.dump(graph, f, indent=2)

    print(f"\n{'=' * 60}")
    print("GRAPH STATISTICS")
    print("=" * 60)
    print(f"  Nodes: {len(nodes)}")
    print(f"  Edges: {len(edges)}")
    print(f"  Topics: {len([n for n in nodes.values() if n['type'] == 'topic'])}")
    print(f"  Concepts: {len([n for n in nodes.values() if n['type'] == 'concept'])}")
    print(f"  Prerequisites: {len([n for n in nodes.values() if n['type'] == 'prerequisite'])}")
    print(f"\nSaved to {GRAPH_FILE}")

    # save full results
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Full results saved to {RESULTS_FILE}")


if __name__ == "__main__":
    main()
