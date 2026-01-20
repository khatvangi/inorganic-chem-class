#!/usr/bin/env python3
"""
analyze_textbooks_v3.py

Robust textbook analysis with quantitative metrics.
Uses keyword matching + statistical analysis (no LLM dependency for core metrics).
LLM only for qualitative synthesis at the end.

Validation criteria:
1. Discriminatory power: Scores vary between books
2. Topic coverage: All 20 topics rated for all books
3. Example counts: Actual numbers, not "many/few"
4. Composite scores: Meaningful rankings

Author: Kiran Brahma + Claude
Date: January 2026
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import Optional
import math

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Filter, FieldCondition, MatchValue, ScrollRequest
    HAS_QDRANT = True
except ImportError:
    HAS_QDRANT = False
    print("Warning: qdrant-client not installed")

# Configuration
QDRANT_URL = "http://localhost:6333"
COLLECTION = "textbooks_chunks"
RESULTS_DIR = Path("experiments/results")

# ============================================================
# TOPIC DEFINITIONS (20 core topics)
# ============================================================

TOPICS = {
    "Atomic Structure": {
        "keywords": ["atomic orbital", "electron configuration", "quantum number",
                    "aufbau", "hund's rule", "pauli exclusion", "shielding",
                    "effective nuclear charge", "penetration", "radial"],
        "weight": 1.0
    },
    "Molecular Orbital Theory": {
        "keywords": ["molecular orbital", "LCAO", "bonding orbital", "antibonding",
                    "bond order", "MO diagram", "HOMO", "LUMO", "σ bond", "π bond"],
        "weight": 1.0
    },
    "Symmetry/Group Theory": {
        "keywords": ["point group", "symmetry operation", "character table",
                    "irreducible representation", "C2v", "Oh", "Td", "D4h",
                    "rotation axis", "reflection plane", "inversion center"],
        "weight": 1.0
    },
    "Acids & Bases": {
        "keywords": ["lewis acid", "bronsted", "hard soft", "HSAB", "pKa",
                    "acidity", "basicity", "amphoteric", "superacid", "pH"],
        "weight": 1.0
    },
    "Redox Chemistry": {
        "keywords": ["oxidation", "reduction", "electrode potential", "redox",
                    "electrochemical", "Nernst", "half-reaction", "galvanic",
                    "electrolysis", "standard potential"],
        "weight": 1.0
    },
    "Coordination Fundamentals": {
        "keywords": ["coordination number", "ligand", "chelate", "dentate",
                    "complex", "werner", "coordination sphere", "isomer",
                    "nomenclature", "IUPAC"],
        "weight": 1.2  # core topic
    },
    "Crystal Field Theory": {
        "keywords": ["crystal field", "d-orbital splitting", "CFSE", "spectrochemical",
                    "Δo", "Δt", "t2g", "eg", "high spin", "low spin",
                    "pairing energy", "Jahn-Teller"],
        "weight": 1.2  # core topic
    },
    "Spectroscopy (UV-Vis, IR, NMR)": {
        "keywords": ["UV-Vis", "infrared", "NMR", "spectroscopy", "absorption",
                    "selection rule", "d-d transition", "charge transfer",
                    "chemical shift", "coupling constant"],
        "weight": 0.8
    },
    "Reaction Mechanisms": {
        "keywords": ["mechanism", "substitution", "SN1", "SN2", "associative",
                    "dissociative", "interchange", "trans effect", "kinetics",
                    "rate law", "activation"],
        "weight": 1.0
    },
    "Main Group (s-block)": {
        "keywords": ["alkali", "alkaline earth", "group 1", "group 2",
                    "sodium", "potassium", "calcium", "magnesium", "lithium",
                    "barium", "cesium"],
        "weight": 1.0
    },
    "Main Group (p-block)": {
        "keywords": ["halogen", "noble gas", "boron", "carbon", "nitrogen",
                    "oxygen", "silicon", "phosphorus", "sulfur", "chlorine",
                    "group 13", "group 14", "group 15", "group 16", "group 17"],
        "weight": 1.0
    },
    "Transition Metals": {
        "keywords": ["transition metal", "d-block", "first row", "iron",
                    "copper", "chromium", "cobalt", "nickel", "manganese",
                    "vanadium", "titanium", "zinc"],
        "weight": 1.0
    },
    "Lanthanides/Actinides": {
        "keywords": ["lanthanide", "actinide", "f-block", "rare earth",
                    "uranium", "cerium", "europium", "gadolinium",
                    "4f orbital", "5f orbital", "lanthanide contraction"],
        "weight": 0.8
    },
    "Organometallics": {
        "keywords": ["organometallic", "metal-carbon", "carbonyl", "alkyl",
                    "18-electron", "oxidative addition", "reductive elimination",
                    "insertion", "Grignard", "ferrocene"],
        "weight": 0.9
    },
    "Bioinorganic": {
        "keywords": ["bioinorganic", "metalloenzyme", "hemoglobin", "cytochrome",
                    "iron-sulfur", "zinc finger", "copper protein", "oxygen transport",
                    "metalloprotein", "cobalamin"],
        "weight": 0.8
    },
    "Solid State": {
        "keywords": ["solid state", "crystal structure", "unit cell", "band theory",
                    "semiconductor", "lattice", "close-packed", "ionic solid",
                    "metallic", "covalent network"],
        "weight": 1.0
    },
    "Catalysis": {
        "keywords": ["catalyst", "catalysis", "homogeneous", "heterogeneous",
                    "turnover", "activation energy", "Wilkinson", "Ziegler-Natta",
                    "hydrogenation", "cross-coupling"],
        "weight": 0.9
    },
    "Materials/Nanochemistry": {
        "keywords": ["nanomaterial", "nanoparticle", "materials chemistry",
                    "quantum dot", "graphene", "carbon nanotube", "MOF",
                    "zeolite", "thin film"],
        "weight": 0.7
    },
    "Environmental IC": {
        "keywords": ["environmental", "pollution", "atmospheric", "remediation",
                    "green chemistry", "ozone", "acid rain", "heavy metal",
                    "water treatment"],
        "weight": 0.6
    },
    "Medicinal IC": {
        "keywords": ["medicinal", "drug", "cisplatin", "therapeutic",
                    "MRI contrast", "radiopharmaceutical", "chelation therapy",
                    "anticancer", "diagnostic"],
        "weight": 0.6
    }
}

# Example detection patterns
EXAMPLE_PATTERNS = [
    r'\bExample\s*\d+',
    r'\bWorked\s+Example',
    r'\bSample\s+Problem',
    r'\bPractice\s+Problem',
    r'\bExercise\s*\d+',
    r'\bSolution[:.]',
    r'\bCalculate\s+the',
    r'\bDetermine\s+the',
    r'\bFind\s+the\s+\w+\s+of',
    r'\bGiven[:.].*\bFind[:.]',
]

# Equation detection patterns
EQUATION_PATTERNS = [
    r'=\s*[\d\w\[\]]+',  # simple equations
    r'Δ[GHSE]°?\s*=',    # thermodynamic
    r'E°\s*=',           # electrochemical
    r'\bΔ[oO]\s*=',      # crystal field
    r'λ\s*=',            # spectroscopy
    r'K[sp|a|b|eq]\s*=', # equilibrium constants
]

# Figure/diagram references
FIGURE_PATTERNS = [
    r'Figure\s*\d+',
    r'Fig\.\s*\d+',
    r'Diagram\s*\d+',
    r'Scheme\s*\d+',
    r'Table\s*\d+',
    r'Chart\s*\d+',
]


@dataclass
class TopicCoverage:
    topic: str
    chunk_count: int
    keyword_hits: int
    keyword_density: float  # hits per 1000 words
    score: int  # 1-5
    rating: str

    def to_dict(self):
        return asdict(self)


@dataclass
class BookAnalysis:
    book_name: str
    total_chunks: int
    total_words: int

    # topic coverage
    topic_scores: dict  # topic -> TopicCoverage

    # examples
    example_count: int
    examples_per_100_chunks: float

    # equations/formulas
    equation_count: int
    equations_per_chunk: float

    # figures
    figure_references: int
    figures_per_chunk: float

    # conceptual density metrics
    avg_words_per_chunk: float
    keyword_diversity: float  # unique keywords / total keywords
    cross_topic_integration: float  # chunks mentioning 2+ topics

    # composite scores
    coverage_score: float  # 0-100
    depth_score: float     # 0-100
    pedagogy_score: float  # 0-100
    overall_score: float   # 0-100

    # rankings
    best_for: list  # e.g., ["theoretical", "coordination"]

    def to_dict(self):
        d = asdict(self)
        d['topic_scores'] = {k: v.to_dict() for k, v in self.topic_scores.items()}
        return d


class TextbookAnalyzer:
    def __init__(self):
        if not HAS_QDRANT:
            raise RuntimeError("qdrant-client required")

        self.client = QdrantClient(url=QDRANT_URL)
        self.results = {}

    def get_book_chunks(self, book_name: str, limit: int = 10000) -> list:
        """Retrieve all chunks for a book."""
        chunks = []
        offset = None

        while True:
            result = self.client.scroll(
                collection_name=COLLECTION,
                scroll_filter=Filter(
                    must=[FieldCondition(
                        key="pdf_name",
                        match=MatchValue(value=book_name)
                    )]
                ),
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )

            batch, next_offset = result
            if not batch:
                break

            for point in batch:
                chunks.append({
                    "id": point.id,
                    "text": point.payload.get("text", ""),
                    "pdf_name": point.payload.get("pdf_name", "")
                })

            if next_offset is None or len(chunks) >= limit:
                break
            offset = next_offset

        return chunks

    def count_keywords(self, text: str, keywords: list) -> int:
        """Count keyword occurrences in text (case-insensitive)."""
        text_lower = text.lower()
        count = 0
        for kw in keywords:
            # use word boundary matching for accuracy
            pattern = r'\b' + re.escape(kw.lower()) + r'\b'
            count += len(re.findall(pattern, text_lower))
        return count

    def count_patterns(self, text: str, patterns: list) -> int:
        """Count pattern matches in text."""
        count = 0
        for pattern in patterns:
            count += len(re.findall(pattern, text, re.IGNORECASE))
        return count

    def calculate_topic_score(self, keyword_density: float) -> tuple:
        """Convert keyword density to 1-5 score."""
        # density thresholds calibrated for STEM textbooks
        if keyword_density >= 15:
            return 5, "excellent"
        elif keyword_density >= 8:
            return 4, "good"
        elif keyword_density >= 3:
            return 3, "fair"
        elif keyword_density >= 1:
            return 2, "limited"
        else:
            return 1, "absent"

    def analyze_book(self, book_name: str) -> BookAnalysis:
        """Perform full analysis on a single book."""
        print(f"\n{'='*60}")
        print(f"Analyzing: {book_name}")
        print(f"{'='*60}")

        # retrieve chunks
        chunks = self.get_book_chunks(book_name)
        if not chunks:
            print(f"  WARNING: No chunks found for {book_name}")
            return None

        print(f"  Retrieved {len(chunks)} chunks")

        # combine all text
        all_text = " ".join(c["text"] for c in chunks)
        total_words = len(all_text.split())

        print(f"  Total words: {total_words:,}")

        # === TOPIC COVERAGE ===
        print(f"  Analyzing topic coverage...")
        topic_scores = {}
        topic_chunks = defaultdict(int)  # topic -> chunks mentioning it

        for topic, config in TOPICS.items():
            keywords = config["keywords"]

            # count chunks and keywords
            topic_chunk_count = 0
            topic_keyword_hits = 0

            for chunk in chunks:
                chunk_hits = self.count_keywords(chunk["text"], keywords)
                if chunk_hits > 0:
                    topic_chunk_count += 1
                    topic_keyword_hits += chunk_hits
                    topic_chunks[topic] += 1

            # calculate density (hits per 1000 words in relevant chunks)
            if topic_chunk_count > 0:
                relevant_words = sum(
                    len(c["text"].split()) for c in chunks
                    if self.count_keywords(c["text"], keywords) > 0
                )
                density = (topic_keyword_hits / max(relevant_words, 1)) * 1000
            else:
                density = 0

            score, rating = self.calculate_topic_score(density)

            topic_scores[topic] = TopicCoverage(
                topic=topic,
                chunk_count=topic_chunk_count,
                keyword_hits=topic_keyword_hits,
                keyword_density=round(density, 2),
                score=score,
                rating=rating
            )

        # === EXAMPLES ===
        print(f"  Counting worked examples...")
        example_count = self.count_patterns(all_text, EXAMPLE_PATTERNS)
        examples_per_100 = (example_count / len(chunks)) * 100 if chunks else 0

        # === EQUATIONS ===
        print(f"  Counting equations...")
        equation_count = self.count_patterns(all_text, EQUATION_PATTERNS)
        equations_per_chunk = equation_count / len(chunks) if chunks else 0

        # === FIGURES ===
        print(f"  Counting figure references...")
        figure_count = self.count_patterns(all_text, FIGURE_PATTERNS)
        figures_per_chunk = figure_count / len(chunks) if chunks else 0

        # === CONCEPTUAL DENSITY ===
        print(f"  Calculating conceptual density...")
        avg_words = total_words / len(chunks) if chunks else 0

        # keyword diversity: unique vs total
        all_keywords = []
        for topic, config in TOPICS.items():
            for kw in config["keywords"]:
                hits = len(re.findall(r'\b' + re.escape(kw.lower()) + r'\b',
                                     all_text.lower()))
                if hits > 0:
                    all_keywords.extend([kw] * hits)

        unique_kw = len(set(all_keywords))
        total_kw = len(all_keywords)
        keyword_diversity = unique_kw / max(total_kw, 1)

        # cross-topic integration: chunks mentioning 2+ topics
        multi_topic_chunks = 0
        for chunk in chunks:
            topics_in_chunk = 0
            for topic, config in TOPICS.items():
                if self.count_keywords(chunk["text"], config["keywords"]) > 0:
                    topics_in_chunk += 1
            if topics_in_chunk >= 2:
                multi_topic_chunks += 1

        cross_topic = multi_topic_chunks / len(chunks) if chunks else 0

        # === COMPOSITE SCORES ===
        print(f"  Computing composite scores...")

        # coverage: average topic score weighted
        weighted_scores = []
        for topic, tc in topic_scores.items():
            weight = TOPICS[topic]["weight"]
            weighted_scores.append(tc.score * weight)
        coverage_score = (sum(weighted_scores) / (5 * sum(TOPICS[t]["weight"] for t in TOPICS))) * 100

        # depth: equations + examples + density
        depth_score = min(100, (
            (equations_per_chunk * 20) +  # up to 5 eq/chunk = 100
            (examples_per_100 * 2) +       # up to 50 ex/100 chunks = 100
            (cross_topic * 100)            # integration bonus
        ) / 3)

        # pedagogy: examples + figures + keyword diversity
        pedagogy_score = min(100, (
            (examples_per_100 * 2) +
            (figures_per_chunk * 50) +
            (keyword_diversity * 100)
        ) / 3)

        # overall: weighted combination
        overall_score = (coverage_score * 0.4 + depth_score * 0.3 + pedagogy_score * 0.3)

        # === BEST FOR ===
        best_for = []

        # check for specializations
        coord_score = topic_scores.get("Coordination Fundamentals", TopicCoverage("", 0, 0, 0, 0, "")).score
        cft_score = topic_scores.get("Crystal Field Theory", TopicCoverage("", 0, 0, 0, 0, "")).score
        if (coord_score + cft_score) / 2 >= 4:
            best_for.append("coordination chemistry")

        mg_s = topic_scores.get("Main Group (s-block)", TopicCoverage("", 0, 0, 0, 0, "")).score
        mg_p = topic_scores.get("Main Group (p-block)", TopicCoverage("", 0, 0, 0, 0, "")).score
        if (mg_s + mg_p) / 2 >= 4:
            best_for.append("main group chemistry")

        if equations_per_chunk > 2:
            best_for.append("theoretical depth")

        if examples_per_100 > 30:
            best_for.append("worked examples")

        if topic_scores.get("Bioinorganic", TopicCoverage("", 0, 0, 0, 0, "")).score >= 4:
            best_for.append("bioinorganic")

        if topic_scores.get("Organometallics", TopicCoverage("", 0, 0, 0, 0, "")).score >= 4:
            best_for.append("organometallics")

        # create result
        analysis = BookAnalysis(
            book_name=book_name,
            total_chunks=len(chunks),
            total_words=total_words,
            topic_scores=topic_scores,
            example_count=example_count,
            examples_per_100_chunks=round(examples_per_100, 1),
            equation_count=equation_count,
            equations_per_chunk=round(equations_per_chunk, 2),
            figure_references=figure_count,
            figures_per_chunk=round(figures_per_chunk, 2),
            avg_words_per_chunk=round(avg_words, 1),
            keyword_diversity=round(keyword_diversity, 3),
            cross_topic_integration=round(cross_topic, 3),
            coverage_score=round(coverage_score, 1),
            depth_score=round(depth_score, 1),
            pedagogy_score=round(pedagogy_score, 1),
            overall_score=round(overall_score, 1),
            best_for=best_for
        )

        print(f"  Done. Overall: {overall_score:.1f}/100")

        return analysis

    def get_all_books(self) -> list:
        """Get list of all books in collection."""
        # scroll through to find unique pdf_names
        books = set()
        offset = None

        while True:
            result = self.client.scroll(
                collection_name=COLLECTION,
                limit=100,
                offset=offset,
                with_payload=["pdf_name"],
                with_vectors=False
            )

            batch, next_offset = result
            if not batch:
                break

            for point in batch:
                pdf_name = point.payload.get("pdf_name")
                if pdf_name:
                    books.add(pdf_name)

            if next_offset is None:
                break
            offset = next_offset

            if len(books) >= 20:  # assume max 20 books
                break

        return sorted(books)

    def analyze_all(self):
        """Analyze all books in collection."""
        books = self.get_all_books()
        print(f"Found {len(books)} books to analyze")

        for book in books:
            analysis = self.analyze_book(book)
            if analysis:
                self.results[book] = analysis

        return self.results

    def save_results(self):
        """Save results to JSON."""
        RESULTS_DIR.mkdir(exist_ok=True)

        # convert to serializable format
        output = {}
        for book, analysis in self.results.items():
            output[book] = analysis.to_dict()

        output_file = RESULTS_DIR / "textbook_analysis_v3.json"
        with open(output_file, "w") as f:
            json.dump(output, f, indent=2)

        print(f"\nResults saved to {output_file}")
        return output_file

    def print_validation_report(self):
        """Print validation report showing discriminatory power."""
        print("\n" + "=" * 70)
        print("VALIDATION REPORT")
        print("=" * 70)

        # Check 1: Score variation
        print("\n--- CHECK 1: Discriminatory Power ---")
        all_coverage = []
        all_depth = []
        all_overall = []

        for book, analysis in self.results.items():
            all_coverage.append(analysis.coverage_score)
            all_depth.append(analysis.depth_score)
            all_overall.append(analysis.overall_score)

        def variation(scores):
            if not scores:
                return 0
            return max(scores) - min(scores)

        print(f"  Coverage score range: {min(all_coverage):.1f} - {max(all_coverage):.1f} (variation: {variation(all_coverage):.1f})")
        print(f"  Depth score range:    {min(all_depth):.1f} - {max(all_depth):.1f} (variation: {variation(all_depth):.1f})")
        print(f"  Overall score range:  {min(all_overall):.1f} - {max(all_overall):.1f} (variation: {variation(all_overall):.1f})")

        has_variation = variation(all_overall) > 10
        print(f"\n  Discriminatory power: {'✓ PASS' if has_variation else '✗ FAIL'}")

        # Check 2: Topic coverage completeness
        print("\n--- CHECK 2: Topic Coverage Completeness ---")
        all_complete = True
        for book, analysis in self.results.items():
            topics_rated = len(analysis.topic_scores)
            if topics_rated < 20:
                print(f"  ✗ {book[:40]}: only {topics_rated}/20 topics")
                all_complete = False

        if all_complete:
            print(f"  ✓ All books have 20/20 topics rated")

        # Check 3: Example counts quantified
        print("\n--- CHECK 3: Example Counts Quantified ---")
        for book, analysis in self.results.items():
            print(f"  {book[:40]:<40} {analysis.example_count:4} examples ({analysis.examples_per_100_chunks:.1f}/100 chunks)")

        # Check 4: Rankings
        print("\n--- CHECK 4: Meaningful Rankings ---")
        ranked = sorted(self.results.items(), key=lambda x: -x[1].overall_score)

        print("\n  Overall Rankings:")
        for i, (book, analysis) in enumerate(ranked, 1):
            best = ", ".join(analysis.best_for[:2]) if analysis.best_for else "general"
            print(f"  {i:2}. {book[:35]:<35} {analysis.overall_score:5.1f}  Best for: {best}")

        print("\n" + "=" * 70)


def main():
    print("=" * 60)
    print("TEXTBOOK ANALYSIS v3 - Quantitative Metrics")
    print("=" * 60)

    analyzer = TextbookAnalyzer()
    analyzer.analyze_all()
    analyzer.save_results()
    analyzer.print_validation_report()


if __name__ == "__main__":
    main()
