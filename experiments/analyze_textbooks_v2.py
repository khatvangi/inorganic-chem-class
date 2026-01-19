#!/usr/bin/env python3
"""
analyze_textbooks_v2.py

Enhanced textbook analysis with conceptual density metrics.
Replaces stamp-counting with STEM-appropriate measurements.

Author: Kiran Brahma + Claude
Date: January 2026
"""

import json
import asyncio
from pathlib import Path
from collections import defaultdict
import re
import httpx

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    HAS_QDRANT = True
except ImportError:
    HAS_QDRANT = False
    print("Warning: qdrant-client not installed")

# Configuration
QDRANT_URL = "http://localhost:6333"
COLLECTION = "textbooks_chunks"
OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen3:latest"
RESULTS_DIR = Path("experiments/results")

# ============================================================
# TOPIC COVERAGE (20 topics)
# ============================================================

TOPIC_COVERAGE_LIST = [
    "Atomic Structure",
    "Molecular Orbital Theory",
    "Symmetry/Group Theory",
    "Acids & Bases",
    "Redox Chemistry",
    "Coordination Fundamentals",
    "Crystal Field Theory",
    "Spectroscopy (UV-Vis, IR, NMR)",
    "Reaction Mechanisms",
    "Main Group (s-block)",
    "Main Group (p-block)",
    "Transition Metals",
    "Lanthanides/Actinides",
    "Organometallics",
    "Bioinorganic",
    "Solid State",
    "Catalysis",
    "Materials/Nanochemistry",
    "Environmental IC",
    "Medicinal IC"
]

TOPIC_KEYWORDS = {
    "Atomic Structure": ["atomic orbital", "electron configuration", "quantum number", "aufbau", "hund", "pauli"],
    "Molecular Orbital Theory": ["molecular orbital", "LCAO", "bonding orbital", "antibonding", "bond order", "MO diagram"],
    "Symmetry/Group Theory": ["point group", "symmetry operation", "character table", "irreducible representation", "C2v", "Oh", "Td"],
    "Acids & Bases": ["lewis acid", "bronsted", "hard soft", "HSAB", "pKa", "acidity"],
    "Redox Chemistry": ["oxidation", "reduction", "electrode potential", "redox", "electrochemical", "Nernst"],
    "Coordination Fundamentals": ["coordination number", "ligand", "chelate", "dentate", "complex", "werner"],
    "Crystal Field Theory": ["crystal field", "d-orbital splitting", "CFSE", "spectrochemical", "delta", "t2g", "eg"],
    "Spectroscopy (UV-Vis, IR, NMR)": ["UV-Vis", "infrared", "NMR", "spectroscopy", "absorption", "selection rule"],
    "Reaction Mechanisms": ["mechanism", "substitution", "SN1", "SN2", "associative", "dissociative", "interchange"],
    "Main Group (s-block)": ["alkali", "alkaline earth", "group 1", "group 2", "sodium", "calcium", "lithium"],
    "Main Group (p-block)": ["halogen", "noble gas", "boron", "carbon", "nitrogen", "oxygen", "silicon", "phosphorus"],
    "Transition Metals": ["transition metal", "d-block", "first row", "iron", "copper", "chromium", "cobalt"],
    "Lanthanides/Actinides": ["lanthanide", "actinide", "f-block", "rare earth", "uranium", "cerium", "4f", "5f"],
    "Organometallics": ["organometallic", "metal-carbon", "carbonyl", "alkyl", "18-electron", "oxidative addition"],
    "Bioinorganic": ["bioinorganic", "metalloenzyme", "hemoglobin", "cytochrome", "iron-sulfur", "zinc finger"],
    "Solid State": ["solid state", "crystal structure", "unit cell", "band theory", "semiconductor", "lattice"],
    "Catalysis": ["catalyst", "catalysis", "homogeneous", "heterogeneous", "turnover", "activation energy"],
    "Materials/Nanochemistry": ["nanomaterial", "nanoparticle", "materials chemistry", "quantum dot", "graphene"],
    "Environmental IC": ["environmental", "pollution", "atmospheric", "remediation", "green chemistry"],
    "Medicinal IC": ["medicinal", "drug", "cisplatin", "therapeutic", "MRI contrast", "radiopharmaceutical"]
}

COVERAGE_SCALE = {
    "excellent": 5,
    "good": 4,
    "fair": 3,
    "limited": 2,
    "absent": 1
}

# ============================================================
# PROMPTS
# ============================================================

TOPIC_COVERAGE_PROMPT = """Analyze this textbook content for coverage of: {topic}

Rate coverage on this scale:
- excellent (5): Comprehensive treatment across multiple sections, full derivations, many examples
- good (4): Solid coverage, worked examples, applications shown
- fair (3): Basic coverage, some examples
- limited (2): Mentioned but not developed
- absent (1): Not covered or only passing reference

Return JSON only:
{{
    "topic": "{topic}",
    "rating": "excellent|good|fair|limited|absent",
    "score": 1-5,
    "evidence": "Brief quote or description supporting rating",
    "depth_indicators": {{
        "derivations_shown": true/false,
        "worked_examples_present": true/false,
        "applications_mentioned": true/false
    }}
}}"""

WORKED_EXAMPLES_PROMPT = """Count worked examples in this textbook section.

A worked example is:
- Explicitly labeled as "Example" or similar
- Shows step-by-step solution
- Has a stated problem and answer

For each example found, record topic area and difficulty (basic/intermediate/advanced).

Return JSON only:
{{
    "examples": [
        {{
            "topic": "topic area",
            "difficulty": "basic|intermediate|advanced",
            "steps": number_of_steps
        }}
    ],
    "total_count": number
}}"""

CONCEPTUAL_DENSITY_PROMPT = """Analyze this passage for conceptual density.

Evaluate:

1. THREAD COMPLETENESS (0-1):
   Does this passage complete a conceptual thread?
   - 1.0: Full derivation chain shown
   - 0.5: Partial chain, some steps assumed
   - 0.0: Orphan concept, no connections

2. INTEGRATION POINTS:
   How many prior concepts must student combine? List them.

3. DERIVATION RATIO (0-1):
   What fraction of equations are derived vs stated?
   - "The formula is..." = stated (0)
   - "Starting from X, we show..." = derived (1)

4. FIGURE INTEGRATION (0-1):
   Are figures explained in text?
   - 1.0: Figure explicitly referenced and explained
   - 0.5: Figure referenced but not explained
   - 0.0: Figure present but not mentioned

Return JSON only:
{{
    "thread_completeness": 0.0-1.0,
    "integration_points": {{
        "count": number,
        "prerequisites": ["list"]
    }},
    "derivation_ratio": 0.0-1.0,
    "figure_integration": 0.0-1.0
}}"""

VISUAL_ANALYSIS_PROMPT = """Analyze visual elements in this textbook section.

Visual types to look for:
- MO diagrams
- Crystal structures
- Reaction schemes
- Energy level diagrams
- Periodic trend plots
- 3D molecular structures
- Phase diagrams
- Spectroscopic data
- Data tables
- Conceptual illustrations

For each figure found, note:
1. Type (from list above)
2. Integration level: comprehensive/adequate/minimal
3. Referenced in text: yes/no

Return JSON only:
{{
    "visual_counts_by_type": {{
        "MO diagrams": number,
        "Crystal structures": number,
        "Energy level diagrams": number,
        "Reaction schemes": number,
        "Data tables": number,
        "Other": number
    }},
    "total_visuals": number,
    "text_integrated_count": number
}}"""

PEDAGOGY_ANALYSIS_PROMPT = """Analyze pedagogical approach in this textbook section.

Evaluate with SPECIFIC EVIDENCE:

1. SCAFFOLDING (1-5):
   - 5: Each concept explicitly builds on named prior concept
   - 3: Implicit progression, prior knowledge assumed
   - 1: Concepts presented in isolation
   Evidence required: Quote showing connection (or absence)

2. PRIOR KNOWLEDGE ASSUMPTIONS:
   List specific concepts assumed known but not reviewed.

3. MISCONCEPTION ADDRESSING (yes/no):
   Does text say "students often think X, but actually Y"?

4. REVIEW ELEMENTS:
   - Summary box present: yes/no
   - Key equations highlighted: yes/no
   - Learning objectives stated: yes/no

Return JSON only:
{{
    "scaffolding_score": 1-5,
    "scaffolding_evidence": "quote or description",
    "prior_knowledge_assumed": ["list"],
    "misconceptions_addressed": true/false,
    "review_elements": {{
        "summary_box": true/false,
        "key_equations": true/false,
        "learning_objectives": true/false
    }}
}}"""


# ============================================================
# ANALYZER CLASS
# ============================================================

class EnhancedTextbookAnalyzer:
    def __init__(self):
        if HAS_QDRANT:
            self.qdrant = QdrantClient(url=QDRANT_URL)
        self.results = {}
        self.semaphore = asyncio.Semaphore(3)  # limit concurrent LLM calls

    def _get_book_list(self) -> list:
        """Get unique book names from Qdrant."""
        if not HAS_QDRANT:
            return []

        # scroll through collection to find unique books
        books = set()
        offset = None

        while True:
            results, offset = self.qdrant.scroll(
                collection_name=COLLECTION,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )

            for point in results:
                book = point.payload.get("pdf_name") or point.payload.get("book") or point.payload.get("source", "unknown")
                if book:
                    books.add(book)

            if offset is None:
                break

        return sorted(books)

    def _get_chunks_for_book(self, book: str, limit: int = 500) -> list:
        """Retrieve chunks for a book."""
        if not HAS_QDRANT:
            return []

        chunks = []
        offset = None

        while len(chunks) < limit:
            results, offset = self.qdrant.scroll(
                collection_name=COLLECTION,
                scroll_filter=Filter(
                    must=[FieldCondition(key="pdf_name", match=MatchValue(value=book))]
                ),
                limit=min(100, limit - len(chunks)),
                offset=offset,
                with_payload=True,
                with_vectors=False
            )

            for point in results:
                chunks.append({
                    "id": point.id,
                    "text": point.payload.get("text", ""),
                    "book": book,
                    "section": point.payload.get("section", ""),
                    "chunk_idx": point.payload.get("chunk_idx", 0)
                })

            if offset is None or len(results) == 0:
                break

        return chunks

    def _filter_chunks_by_keywords(self, chunks: list, topic: str) -> list:
        """Filter chunks likely to contain topic."""
        keywords = TOPIC_KEYWORDS.get(topic, [topic.lower()])
        relevant = []

        for chunk in chunks:
            text_lower = chunk["text"].lower()
            if any(kw.lower() in text_lower for kw in keywords):
                relevant.append(chunk)

        return relevant

    def _likely_contains_example(self, text: str) -> bool:
        """Check if text likely contains worked example."""
        patterns = [
            r'\bexample\b', r'\bworked\b', r'\bsolution\b',
            r'\bstep\s+\d', r'\bcalculate\b', r'\bdetermine\b'
        ]
        text_lower = text.lower()
        return any(re.search(p, text_lower) for p in patterns)

    def _likely_contains_figure(self, text: str) -> bool:
        """Check if text references figures."""
        patterns = [
            r'\bfigure\b', r'\bfig\.\b', r'\bdiagram\b',
            r'\bscheme\b', r'\btable\b', r'\bstructure\b'
        ]
        text_lower = text.lower()
        return any(re.search(p, text_lower) for p in patterns)

    def _stratified_sample(self, chunks: list, n: int) -> list:
        """Sample chunks from different parts of book."""
        if len(chunks) <= n:
            return chunks

        # Sort by chunk_idx and sample evenly
        sorted_chunks = sorted(chunks, key=lambda c: c.get("chunk_idx", 0))
        step = len(sorted_chunks) // n
        return [sorted_chunks[i * step] for i in range(n)]

    def _avg(self, items: list, key: str) -> float:
        """Calculate average for nested key."""
        values = []
        for item in items:
            val = item
            for k in key.split("."):
                if isinstance(val, dict):
                    val = val.get(k, 0)
                else:
                    val = 0
                    break
            if isinstance(val, (int, float)):
                values.append(val)
        return sum(values) / max(len(values), 1)

    def _pct_true(self, items: list, key: str) -> float:
        """Calculate percentage of True values for nested key."""
        count = 0
        total = 0
        for item in items:
            val = item
            for k in key.split("."):
                if isinstance(val, dict):
                    val = val.get(k, False)
                else:
                    val = False
                    break
            if val is True:
                count += 1
            total += 1
        return count / max(total, 1)

    def _count_by_key(self, items: list, key: str) -> dict:
        """Count items by key value."""
        counts = defaultdict(int)
        for item in items:
            val = item.get(key, "unknown")
            counts[val] += 1
        return dict(counts)

    def _aggregate_lists(self, items: list, key: str) -> list:
        """Aggregate list values across items."""
        all_values = []
        for item in items:
            val = item
            for k in key.split("."):
                if isinstance(val, dict):
                    val = val.get(k, [])
                else:
                    val = []
                    break
            if isinstance(val, list):
                all_values.extend(val)

        # Return most common
        counts = defaultdict(int)
        for v in all_values:
            counts[v] += 1
        return sorted(counts.keys(), key=lambda x: -counts[x])[:10]

    async def _query_llm(self, prompt: str, context: str) -> str:
        """Query Ollama with prompt and context."""
        async with self.semaphore:
            try:
                async with httpx.AsyncClient(timeout=120) as client:
                    response = await client.post(
                        f"{OLLAMA_URL}/api/generate",
                        json={
                            "model": MODEL,
                            "prompt": f"{prompt}\n\nCONTEXT:\n{context[:4000]}\n\nRespond with JSON only, no markdown.",
                            "stream": False,
                            "options": {"temperature": 0.1}
                        }
                    )
                    result = response.json()["response"]
                    # Clean up response - extract JSON
                    result = result.strip()
                    if result.startswith("```"):
                        result = re.sub(r'^```\w*\n?', '', result)
                        result = re.sub(r'\n?```$', '', result)
                    return result
            except Exception as e:
                print(f"  LLM error: {e}")
                return "{}"

    async def _analyze_topic_coverage(self, book: str, chunks: list) -> dict:
        """Rate coverage for all 20 topics."""
        coverage = {}

        for topic in TOPIC_COVERAGE_LIST:
            print(f"    Analyzing topic: {topic}")
            relevant_chunks = self._filter_chunks_by_keywords(chunks, topic)

            if not relevant_chunks:
                coverage[topic] = {
                    "rating": "absent",
                    "score": 1,
                    "evidence": "No chunks matched topic keywords"
                }
                continue

            # Analyze sample of relevant chunks
            sample = relevant_chunks[:10]
            combined_text = "\n\n---\n\n".join([c["text"] for c in sample])

            prompt = TOPIC_COVERAGE_PROMPT.format(topic=topic)
            response = await self._query_llm(prompt, combined_text)

            try:
                result = json.loads(response)
                coverage[topic] = result
            except json.JSONDecodeError:
                coverage[topic] = {
                    "rating": "fair",
                    "score": 3,
                    "evidence": f"Found {len(relevant_chunks)} chunks but couldn't parse analysis"
                }

        return coverage

    async def _count_worked_examples(self, chunks: list) -> dict:
        """Quantified example counting."""
        all_examples = []

        # Filter to chunks likely containing examples
        example_chunks = [c for c in chunks if self._likely_contains_example(c["text"])]
        print(f"    Found {len(example_chunks)} chunks with potential examples")

        # Sample if too many
        sample = example_chunks[:30] if len(example_chunks) > 30 else example_chunks

        for chunk in sample:
            response = await self._query_llm(WORKED_EXAMPLES_PROMPT, chunk["text"])
            try:
                result = json.loads(response)
                examples = result.get("examples", [])
                all_examples.extend(examples)
            except json.JSONDecodeError:
                continue

        return {
            "total_count": len(all_examples),
            "by_difficulty": self._count_by_key(all_examples, "difficulty"),
            "by_topic": self._count_by_key(all_examples, "topic"),
            "avg_steps": sum(e.get("steps", 0) for e in all_examples) / max(len(all_examples), 1),
            "chunks_analyzed": len(sample)
        }

    async def _measure_conceptual_density(self, chunks: list) -> dict:
        """Calculate conceptual density scores."""
        densities = []

        sample = self._stratified_sample(chunks, n=30)
        print(f"    Analyzing density for {len(sample)} chunks")

        for chunk in sample:
            response = await self._query_llm(CONCEPTUAL_DENSITY_PROMPT, chunk["text"])
            try:
                result = json.loads(response)
                densities.append(result)
            except json.JSONDecodeError:
                continue

        # Calculate composite
        avg_thread = self._avg(densities, "thread_completeness")
        avg_deriv = self._avg(densities, "derivation_ratio")
        avg_fig = self._avg(densities, "figure_integration")
        composite = (avg_thread + avg_deriv + avg_fig) / 3

        return {
            "avg_thread_completeness": round(avg_thread, 3),
            "avg_integration_points": round(self._avg(densities, "integration_points.count"), 2),
            "avg_derivation_ratio": round(avg_deriv, 3),
            "avg_figure_integration": round(avg_fig, 3),
            "composite_density": round(composite, 3),
            "sample_size": len(densities)
        }

    async def _analyze_visuals(self, chunks: list) -> dict:
        """Type-specific visual analysis."""
        visual_counts = defaultdict(int)
        integrated_count = 0

        figure_chunks = [c for c in chunks if self._likely_contains_figure(c["text"])]
        print(f"    Found {len(figure_chunks)} chunks with potential figures")

        sample = figure_chunks[:25] if len(figure_chunks) > 25 else figure_chunks

        for chunk in sample:
            response = await self._query_llm(VISUAL_ANALYSIS_PROMPT, chunk["text"])
            try:
                result = json.loads(response)
                for vtype, count in result.get("visual_counts_by_type", {}).items():
                    visual_counts[vtype] += count
                integrated_count += result.get("text_integrated_count", 0)
            except json.JSONDecodeError:
                continue

        total = sum(visual_counts.values())
        return {
            "counts_by_type": dict(visual_counts),
            "total": total,
            "text_integrated": integrated_count,
            "quality_score": round(integrated_count / max(total, 1), 3),
            "dominant_type": max(visual_counts, key=visual_counts.get) if visual_counts else None,
            "chunks_analyzed": len(sample)
        }

    async def _analyze_pedagogy(self, chunks: list) -> dict:
        """Discriminatory pedagogy metrics."""
        pedagogy_results = []

        sample = self._stratified_sample(chunks, n=25)
        print(f"    Analyzing pedagogy for {len(sample)} chunks")

        for chunk in sample:
            response = await self._query_llm(PEDAGOGY_ANALYSIS_PROMPT, chunk["text"])
            try:
                result = json.loads(response)
                pedagogy_results.append(result)
            except json.JSONDecodeError:
                continue

        return {
            "avg_scaffolding": round(self._avg(pedagogy_results, "scaffolding_score"), 2),
            "misconceptions_addressed_pct": round(self._pct_true(pedagogy_results, "misconceptions_addressed"), 3),
            "review_elements": {
                "summary_box_pct": round(self._pct_true(pedagogy_results, "review_elements.summary_box"), 3),
                "key_equations_pct": round(self._pct_true(pedagogy_results, "review_elements.key_equations"), 3),
                "learning_objectives_pct": round(self._pct_true(pedagogy_results, "review_elements.learning_objectives"), 3),
            },
            "common_prior_knowledge": self._aggregate_lists(pedagogy_results, "prior_knowledge_assumed"),
            "sample_size": len(pedagogy_results)
        }

    def _calculate_composites(self, book_results: dict, chunk_count: int) -> dict:
        """Calculate overall composite scores."""
        topic_cov = book_results["topic_coverage"]
        density = book_results["conceptual_density"]
        pedagogy = book_results["pedagogy"]
        examples = book_results["worked_examples"]

        # Topic coverage score
        topic_scores = [t.get("score", 1) for t in topic_cov.values() if isinstance(t, dict)]
        topic_coverage_score = sum(topic_scores) / max(len(topic_scores), 1)

        # Normalize
        return {
            "topic_coverage_normalized": round(topic_coverage_score / 5, 3),
            "conceptual_density_normalized": density.get("composite_density", 0),
            "pedagogy_normalized": round(pedagogy.get("avg_scaffolding", 1) / 5, 3),
            "examples_per_100_chunks": round(examples["total_count"] / max(chunk_count, 1) * 100, 2),
            "overall_quality": round(
                topic_coverage_score / 5 * 0.3 +
                density.get("composite_density", 0) * 0.3 +
                pedagogy.get("avg_scaffolding", 1) / 5 * 0.2 +
                min(examples["total_count"] / 100, 1) * 0.2,
                3
            )
        }

    async def analyze_all_books(self):
        """Run all analysis dimensions for all textbooks."""
        import sys
        books = self._get_book_list()

        if not books:
            print("No books found in Qdrant. Check collection name.", flush=True)
            return {}

        print(f"Found {len(books)} books to analyze", flush=True)
        sys.stdout.flush()

        for book in books:
            print(f"\n{'='*60}", flush=True)
            print(f"Analyzing: {book}", flush=True)
            print(f"{'='*60}", flush=True)
            sys.stdout.flush()

            chunks = self._get_chunks_for_book(book, limit=500)
            print(f"  Retrieved {len(chunks)} chunks", flush=True)
            sys.stdout.flush()

            if not chunks:
                print(f"  Skipping - no chunks found", flush=True)
                continue

            print("  [1/5] Topic coverage...", flush=True)
            sys.stdout.flush()
            topic_coverage = await self._analyze_topic_coverage(book, chunks)

            print("  [2/5] Worked examples...", flush=True)
            sys.stdout.flush()
            worked_examples = await self._count_worked_examples(chunks)

            print("  [3/5] Conceptual density...", flush=True)
            sys.stdout.flush()
            conceptual_density = await self._measure_conceptual_density(chunks)

            print("  [4/5] Visual analysis...", flush=True)
            sys.stdout.flush()
            visual_analysis = await self._analyze_visuals(chunks)

            print("  [5/5] Pedagogy analysis...", flush=True)
            sys.stdout.flush()
            pedagogy = await self._analyze_pedagogy(chunks)

            self.results[book] = {
                "basic_info": {
                    "chunks": len(chunks),
                    "book_name": book
                },
                "topic_coverage": topic_coverage,
                "worked_examples": worked_examples,
                "conceptual_density": conceptual_density,
                "visual_analysis": visual_analysis,
                "pedagogy": pedagogy,
            }

            # Calculate composite scores
            self.results[book]["composite_scores"] = self._calculate_composites(
                self.results[book], len(chunks)
            )

            print(f"  Done. Overall quality: {self.results[book]['composite_scores']['overall_quality']}")

        self._save_results()
        self._generate_comparison_matrix()
        return self.results

    def _save_results(self):
        """Save full results."""
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

        with open(RESULTS_DIR / "textbook_analysis_v2.json", "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\nResults saved to {RESULTS_DIR / 'textbook_analysis_v2.json'}")

    def _generate_comparison_matrix(self):
        """Generate side-by-side comparison."""
        matrix = []

        for book, data in self.results.items():
            row = {
                "book": book.replace(".pdf", "")[:20],
                "chunks": data["basic_info"]["chunks"],
            }

            # Add topic scores for key topics
            for topic in ["Molecular Orbital Theory", "Crystal Field Theory",
                          "Coordination Fundamentals", "Main Group (s-block)", "Main Group (p-block)"]:
                score = data["topic_coverage"].get(topic, {}).get("score", 0)
                row[topic[:15]] = score

            # Key metrics
            row["density"] = data["conceptual_density"]["composite_density"]
            row["examples"] = data["worked_examples"]["total_count"]
            row["scaffolding"] = data["pedagogy"]["avg_scaffolding"]
            row["derivation"] = data["conceptual_density"]["avg_derivation_ratio"]
            row["overall"] = data["composite_scores"]["overall_quality"]

            matrix.append(row)

        # Sort by overall quality
        matrix = sorted(matrix, key=lambda x: -x["overall"])

        # Save JSON
        with open(RESULTS_DIR / "textbook_comparison_matrix.json", "w") as f:
            json.dump(matrix, f, indent=2)

        # Save markdown
        self._save_markdown_table(matrix)

    def _save_markdown_table(self, matrix: list):
        """Save comparison as markdown table."""
        if not matrix:
            return

        md = "# Textbook Comparison Matrix\n\n"
        md += "*Generated from enhanced analysis*\n\n"

        # Header
        cols = ["book", "chunks", "Molecular Orbita", "Crystal Field T",
                "Coordination Fu", "Main Group (s-b", "Main Group (p-b",
                "density", "examples", "scaffolding", "overall"]

        md += "| " + " | ".join(cols) + " |\n"
        md += "|" + "|".join(["---"] * len(cols)) + "|\n"

        for row in matrix:
            values = [str(row.get(c, ""))[:15] for c in cols]
            md += "| " + " | ".join(values) + " |\n"

        md += "\n\n## Key\n\n"
        md += "- **density**: Composite conceptual density (0-1)\n"
        md += "- **examples**: Total worked examples found\n"
        md += "- **scaffolding**: Pedagogical scaffolding score (1-5)\n"
        md += "- **overall**: Weighted overall quality (0-1)\n"

        with open(RESULTS_DIR / "textbook_comparison_matrix.md", "w") as f:
            f.write(md)

        print(f"Comparison matrix saved to {RESULTS_DIR / 'textbook_comparison_matrix.md'}")


async def main():
    import sys
    print("="*60, flush=True)
    print("ENHANCED TEXTBOOK ANALYSIS v2", flush=True)
    print("="*60, flush=True)
    sys.stdout.flush()

    if not HAS_QDRANT:
        print("Error: qdrant-client required. Install with: pip install qdrant-client", flush=True)
        return

    analyzer = EnhancedTextbookAnalyzer()
    results = await analyzer.analyze_all_books()

    print("\n" + "="*60, flush=True)
    print("ANALYSIS COMPLETE", flush=True)
    print("="*60, flush=True)
    print(f"Books analyzed: {len(results)}", flush=True)
    print(f"Results: {RESULTS_DIR / 'textbook_analysis_v2.json'}", flush=True)
    print(f"Matrix: {RESULTS_DIR / 'textbook_comparison_matrix.md'}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
