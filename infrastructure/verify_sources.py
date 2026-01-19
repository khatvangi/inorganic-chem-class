#!/usr/bin/env python3
"""
Chemistry Curriculum Infrastructure: Source Verification Layer

verifies what textbooks are actually in Qdrant before any curriculum generation.
produces a verified manifest that downstream tools can trust.

usage:
    python verify_sources.py [collection_name] [--output manifest.json]
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

try:
    from qdrant_client import QdrantClient
except ImportError:
    print("ERROR: qdrant-client not installed. Run: pip install qdrant-client")
    sys.exit(1)


QDRANT_URL = "http://localhost:6333"


def verify_collection(collection_name: str) -> dict:
    """
    scan entire collection and build verified manifest of sources.
    returns dict with source counts, sample content, and verification status.
    """
    client = QdrantClient(url=QDRANT_URL)

    # check collection exists
    collections = client.get_collections().collections
    collection_names = [c.name for c in collections]

    if collection_name not in collection_names:
        return {
            "status": "ERROR",
            "error": f"Collection '{collection_name}' not found",
            "available_collections": collection_names
        }

    # get collection info
    info = client.get_collection(collection_name)
    total_points = info.points_count

    # scroll through ALL points
    sources = defaultdict(lambda: {"count": 0, "samples": [], "chunk_indices": []})
    offset = None
    scanned = 0

    print(f"Scanning {total_points} points in '{collection_name}'...")

    while True:
        results, offset = client.scroll(
            collection_name=collection_name,
            limit=1000,
            offset=offset,
            with_payload=True
        )

        for point in results:
            payload = point.payload
            # try multiple possible field names for source
            pdf_name = (
                payload.get('pdf_name') or
                payload.get('source') or
                payload.get('filename') or
                payload.get('book') or
                'UNKNOWN'
            )

            sources[pdf_name]["count"] += 1

            # collect sample text (first 3 per source)
            if len(sources[pdf_name]["samples"]) < 3:
                text = payload.get('text', payload.get('content', ''))[:200]
                sources[pdf_name]["samples"].append(text)

            # track chunk indices
            chunk_idx = payload.get('chunk_idx', payload.get('chunk_id', scanned))
            if len(sources[pdf_name]["chunk_indices"]) < 10:
                sources[pdf_name]["chunk_indices"].append(chunk_idx)

            scanned += 1

        print(f"  Scanned {scanned}/{total_points}...", end='\r')

        if offset is None:
            break

    print(f"\nDone. Found {len(sources)} unique sources.")

    # build manifest
    manifest = {
        "status": "VERIFIED",
        "verification_timestamp": datetime.now().isoformat(),
        "collection": collection_name,
        "total_points": total_points,
        "scanned_points": scanned,
        "unique_sources": len(sources),
        "sources": {}
    }

    for src, data in sorted(sources.items(), key=lambda x: -x[1]["count"]):
        manifest["sources"][src] = {
            "chunk_count": data["count"],
            "percentage": round(100 * data["count"] / total_points, 2),
            "sample_text": data["samples"][0][:100] if data["samples"] else "",
            "verified": data["count"] > 0
        }

    return manifest


def print_manifest(manifest: dict):
    """pretty print the verification manifest"""
    if manifest["status"] == "ERROR":
        print(f"\n❌ ERROR: {manifest['error']}")
        if "available_collections" in manifest:
            print(f"   Available: {manifest['available_collections']}")
        return

    print(f"\n{'='*60}")
    print(f"VERIFIED SOURCE MANIFEST")
    print(f"{'='*60}")
    print(f"Collection:    {manifest['collection']}")
    print(f"Total Points:  {manifest['total_points']:,}")
    print(f"Unique Sources: {manifest['unique_sources']}")
    print(f"Verified At:   {manifest['verification_timestamp']}")
    print(f"{'='*60}")
    print(f"\n{'Source':<45} {'Chunks':>8} {'%':>7}")
    print(f"{'-'*60}")

    for src, data in manifest["sources"].items():
        status = "✓" if data["verified"] else "?"
        print(f"{status} {src:<43} {data['chunk_count']:>8,} {data['percentage']:>6.1f}%")

    print(f"{'-'*60}")
    print(f"  TOTAL: {manifest['total_points']:,} chunks from {manifest['unique_sources']} sources")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Verify Qdrant collection sources")
    parser.add_argument("collection", nargs="?", default="textbooks_chunks",
                        help="Qdrant collection name (default: textbooks_chunks)")
    parser.add_argument("--output", "-o", help="Output JSON file for manifest")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress progress output")
    args = parser.parse_args()

    manifest = verify_collection(args.collection)

    if not args.quiet:
        print_manifest(manifest)

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"\nManifest saved to: {args.output}")

    # exit with error code if verification failed
    sys.exit(0 if manifest["status"] == "VERIFIED" else 1)


if __name__ == "__main__":
    main()
