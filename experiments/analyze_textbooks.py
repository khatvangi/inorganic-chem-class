#!/usr/bin/env python3
"""
Textbook Style Analysis
Analyzes each textbook for pedagogy, presentation style, strengths, weaknesses.

This creates a "fingerprint" of each book's teaching approach to preserve
unique voices when synthesizing content.
"""

import json
import random
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
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# sample size per book
SAMPLES_PER_BOOK = 25

client = QdrantClient(url=QDRANT_URL)


def query_llm(prompt: str, temperature: float = 0.3) -> str:
    """query Qwen3 for analysis"""
    full_prompt = f"{prompt}\n\n/no_think"

    url = f"{OLLAMA_URL}/api/generate"
    data = json.dumps({
        "model": MODEL,
        "prompt": full_prompt,
        "stream": False,
        "options": {"temperature": temperature}
    }).encode('utf-8')

    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('response', '')
    except Exception as e:
        return f"[ERROR: {e}]"


def get_books():
    """get list of books with chunk counts"""
    results, _ = client.scroll(
        collection_name=COLLECTION,
        limit=10000,
        with_payload=True,
        with_vectors=False
    )

    books = defaultdict(list)
    for point in results:
        book = point.payload.get('pdf_name', 'unknown')
        books[book].append(point)

    # filter to books with substantial content
    return {k: v for k, v in books.items() if len(v) >= 50}


def sample_chunks(points, n=SAMPLES_PER_BOOK):
    """sample diverse chunks from a book"""
    if len(points) <= n:
        return points

    # stratified sampling: early, middle, late sections
    sorted_points = sorted(points, key=lambda p: p.payload.get('chunk_idx', 0))

    # divide into thirds
    third = len(sorted_points) // 3
    early = sorted_points[:third]
    middle = sorted_points[third:2*third]
    late = sorted_points[2*third:]

    samples = []
    for section in [early, middle, late]:
        if section:
            k = min(n // 3 + 1, len(section))
            samples.extend(random.sample(section, k))

    return samples[:n]


def analyze_pedagogy(book_name: str, chunks: list) -> dict:
    """analyze pedagogical approach"""

    # combine sample texts
    sample_texts = []
    for chunk in chunks[:10]:
        text = chunk.payload.get('text', '')[:1500]
        sample_texts.append(text)

    combined = "\n---\n".join(sample_texts)

    prompt = f"""Analyze the PEDAGOGICAL APPROACH of this inorganic chemistry textbook based on these sample passages.

TEXTBOOK: {book_name}

SAMPLE PASSAGES:
\"\"\"
{combined}
\"\"\"

Analyze and provide a JSON response with:
{{
    "teaching_philosophy": "describe the overall teaching approach (e.g., theoretical-first, example-driven, historical, applications-focused)",
    "difficulty_level": "introductory | intermediate | advanced",
    "assumed_prerequisites": ["list prerequisites the book assumes"],
    "learning_progression": "how does the book build concepts? (linear, spiral, modular)",
    "cognitive_load": "low | medium | high - how dense is the information?",
    "active_learning": "does it include exercises, questions, worked examples? describe",
    "scaffolding": "how does it support learner understanding?"
}}

Return ONLY valid JSON."""

    response = query_llm(prompt)
    try:
        # extract JSON from response
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except:
        pass
    return {"raw_response": response}


def analyze_presentation_style(book_name: str, chunks: list) -> dict:
    """analyze presentation and writing style"""

    sample_texts = []
    for chunk in chunks[5:15]:
        text = chunk.payload.get('text', '')[:1500]
        sample_texts.append(text)

    combined = "\n---\n".join(sample_texts)

    prompt = f"""Analyze the PRESENTATION STYLE of this inorganic chemistry textbook.

TEXTBOOK: {book_name}

SAMPLE PASSAGES:
\"\"\"
{combined}
\"\"\"

Analyze and provide a JSON response:
{{
    "writing_tone": "formal/academic | conversational | technical | accessible",
    "sentence_complexity": "simple | moderate | complex",
    "use_of_analogies": "none | occasional | frequent - give examples if found",
    "narrative_style": "descriptive | explanatory | argumentative | mixed",
    "use_of_examples": "abstract | concrete | real-world applications",
    "visual_references": "does it reference figures, diagrams, structures frequently?",
    "mathematical_rigor": "qualitative | semi-quantitative | highly quantitative",
    "distinctive_features": ["list 2-3 unique stylistic features"],
    "sample_characteristic_sentence": "quote one sentence that exemplifies the style"
}}

Return ONLY valid JSON."""

    response = query_llm(prompt)
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except:
        pass
    return {"raw_response": response}


def analyze_strengths_weaknesses(book_name: str, chunks: list) -> dict:
    """analyze strengths and weaknesses"""

    sample_texts = []
    for chunk in chunks[10:20]:
        text = chunk.payload.get('text', '')[:1500]
        sample_texts.append(text)

    combined = "\n---\n".join(sample_texts)

    prompt = f"""Analyze the STRENGTHS and WEAKNESSES of this inorganic chemistry textbook for undergraduate teaching.

TEXTBOOK: {book_name}

SAMPLE PASSAGES:
\"\"\"
{combined}
\"\"\"

Provide a JSON response:
{{
    "strengths": [
        "strength 1 with specific evidence",
        "strength 2 with specific evidence",
        "strength 3 with specific evidence"
    ],
    "weaknesses": [
        "weakness 1 with specific evidence",
        "weakness 2 with specific evidence"
    ],
    "best_used_for": "describe ideal use case (e.g., 'introduction to topic X', 'deep dive into Y', 'exam preparation')",
    "complements_well_with": "what type of resource would complement this book?",
    "topic_coverage_quality": {{
        "coordination_chemistry": "excellent | good | fair | limited",
        "main_group": "excellent | good | fair | limited",
        "solid_state": "excellent | good | fair | limited",
        "thermodynamics": "excellent | good | fair | limited"
    }},
    "overall_rating": "1-10 for undergraduate inorganic chemistry"
}}

Return ONLY valid JSON."""

    response = query_llm(prompt)
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except:
        pass
    return {"raw_response": response}


def analyze_visual_elements(book_name: str, chunks: list) -> dict:
    """analyze use of visual elements based on text references"""

    sample_texts = []
    for chunk in chunks[:20]:
        text = chunk.payload.get('text', '')
        sample_texts.append(text)

    combined = "\n---\n".join(sample_texts)

    # count visual references
    visual_keywords = ['figure', 'fig.', 'diagram', 'table', 'chart', 'structure',
                       'scheme', 'illustration', 'image', 'plot', 'graph']

    text_lower = combined.lower()
    visual_refs = sum(text_lower.count(kw) for kw in visual_keywords)

    prompt = f"""Analyze how this textbook uses VISUAL ELEMENTS based on these passages.

TEXTBOOK: {book_name}
Visual references found: {visual_refs} in sample

SAMPLE PASSAGES:
\"\"\"
{combined[:8000]}
\"\"\"

Provide a JSON response:
{{
    "visual_density": "low | medium | high",
    "figure_types": ["list types of visuals mentioned: orbital diagrams, crystal structures, reaction schemes, etc."],
    "integration_quality": "how well are visuals integrated with text explanations?",
    "visual_pedagogy": "are visuals decorative or essential for understanding?",
    "notable_visual_approaches": "any distinctive visual teaching methods?"
}}

Return ONLY valid JSON."""

    response = query_llm(prompt)
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            result = json.loads(response[start:end])
            result['visual_reference_count'] = visual_refs
            return result
    except:
        pass
    return {"raw_response": response, "visual_reference_count": visual_refs}


def analyze_explanation_depth(book_name: str, chunks: list) -> dict:
    """analyze whether book explains WHY vs just WHAT"""

    sample_texts = []
    for chunk in chunks[5:20]:
        text = chunk.payload.get('text', '')[:1500]
        sample_texts.append(text)

    combined = "\n---\n".join(sample_texts)

    prompt = f"""Analyze the EXPLANATION DEPTH of this inorganic chemistry textbook.

TEXTBOOK: {book_name}

SAMPLE PASSAGES:
\"\"\"
{combined}
\"\"\"

Evaluate whether the book explains:
- WHY things happen (mechanistic, causal reasoning)
- Or just WHAT happens (descriptive, fact-listing)

Provide a JSON response:
{{
    "explanation_type": "mechanistic | descriptive | mixed",
    "causal_reasoning": "strong | moderate | weak - does it explain cause-effect relationships?",
    "molecular_level_detail": "does it explain at the electron/orbital level?",
    "conceptual_depth": "surface | moderate | deep",
    "why_vs_what_ratio": "estimate percentage of 'why' explanations (0-100)",
    "example_of_deep_explanation": "quote a passage showing deep explanation if found",
    "example_of_shallow_explanation": "quote a passage showing surface-level description if found"
}}

Return ONLY valid JSON."""

    response = query_llm(prompt)
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except:
        pass
    return {"raw_response": response}


def analyze_problem_solving(book_name: str, chunks: list) -> dict:
    """analyze problem-solving pedagogy"""

    sample_texts = []
    for chunk in chunks:
        text = chunk.payload.get('text', '')[:1500]
        sample_texts.append(text)

    combined = "\n---\n".join(sample_texts)

    # count problem-solving indicators
    problem_keywords = ['example', 'problem', 'solution', 'calculate', 'determine',
                        'step 1', 'step 2', 'exercise', 'practice', 'try this']
    text_lower = combined.lower()
    problem_refs = sum(text_lower.count(kw) for kw in problem_keywords)

    prompt = f"""Analyze the PROBLEM-SOLVING APPROACH of this inorganic chemistry textbook.

TEXTBOOK: {book_name}
Problem-solving keywords found: {problem_refs}

SAMPLE PASSAGES:
\"\"\"
{combined[:8000]}
\"\"\"

Provide a JSON response:
{{
    "worked_examples": "none | few | moderate | many",
    "step_by_step_solutions": "does it show detailed solution steps?",
    "scaffolded_practice": "does difficulty increase gradually?",
    "problem_types": ["list types: numerical, conceptual, prediction, comparison, etc."],
    "self_check_questions": "are there questions for students to test understanding?",
    "answer_availability": "are answers provided? partial solutions?",
    "problem_solving_strategy": "does it teach HOW to approach problems, not just solve them?"
}}

Return ONLY valid JSON."""

    response = query_llm(prompt)
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            result = json.loads(response[start:end])
            result['problem_keyword_count'] = problem_refs
            return result
    except:
        pass
    return {"raw_response": response, "problem_keyword_count": problem_refs}


def analyze_real_world_connections(book_name: str, chunks: list) -> dict:
    """analyze real-world applications and connections"""

    sample_texts = []
    for chunk in chunks:
        text = chunk.payload.get('text', '')[:1500]
        sample_texts.append(text)

    combined = "\n---\n".join(sample_texts)

    # count application indicators
    app_keywords = ['application', 'industry', 'industrial', 'medicine', 'drug',
                    'pharmaceutical', 'catalyst', 'material', 'technology',
                    'environment', 'pollution', 'everyday', 'practical']
    text_lower = combined.lower()
    app_refs = sum(text_lower.count(kw) for kw in app_keywords)

    prompt = f"""Analyze the REAL-WORLD CONNECTIONS in this inorganic chemistry textbook.

TEXTBOOK: {book_name}
Application keywords found: {app_refs}

SAMPLE PASSAGES:
\"\"\"
{combined[:8000]}
\"\"\"

Provide a JSON response:
{{
    "application_density": "rare | occasional | frequent | pervasive",
    "application_domains": ["list domains: industrial, medical, environmental, materials, etc."],
    "specific_examples": ["list 2-3 specific real-world examples mentioned"],
    "integration_style": "separate boxed sections | woven into main text | chapter endings",
    "career_relevance": "does it mention careers or professional applications?",
    "current_research": "does it reference recent discoveries or ongoing research?",
    "societal_impact": "does it discuss broader impacts of chemistry?"
}}

Return ONLY valid JSON."""

    response = query_llm(prompt)
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            result = json.loads(response[start:end])
            result['application_keyword_count'] = app_refs
            return result
    except:
        pass
    return {"raw_response": response, "application_keyword_count": app_refs}


def analyze_historical_context(book_name: str, chunks: list) -> dict:
    """analyze historical and contextual content"""

    sample_texts = []
    for chunk in chunks:
        text = chunk.payload.get('text', '')[:1500]
        sample_texts.append(text)

    combined = "\n---\n".join(sample_texts)

    # count historical indicators
    hist_keywords = ['discovered', 'history', 'historical', 'scientist', 'nobel',
                     'century', '1800', '1900', 'development', 'evolution']
    text_lower = combined.lower()
    hist_refs = sum(text_lower.count(kw) for kw in hist_keywords)

    prompt = f"""Analyze the HISTORICAL CONTEXT in this inorganic chemistry textbook.

TEXTBOOK: {book_name}
Historical keywords found: {hist_refs}

SAMPLE PASSAGES:
\"\"\"
{combined[:8000]}
\"\"\"

Provide a JSON response:
{{
    "historical_content": "none | minimal | moderate | rich",
    "discovery_narratives": "does it tell stories of how concepts were discovered?",
    "scientist_mentions": ["list any scientists mentioned by name"],
    "evolution_of_ideas": "does it show how understanding evolved over time?",
    "contextual_motivation": "does history help explain WHY we study certain topics?",
    "notable_historical_passages": "quote any particularly good historical content if found"
}}

Return ONLY valid JSON."""

    response = query_llm(prompt)
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            result = json.loads(response[start:end])
            result['historical_keyword_count'] = hist_refs
            return result
    except:
        pass
    return {"raw_response": response, "historical_keyword_count": hist_refs}


def compute_readability_metrics(chunks: list) -> dict:
    """compute quantitative readability metrics"""
    import re

    all_text = " ".join(chunk.payload.get('text', '') for chunk in chunks)

    # basic metrics
    sentences = re.split(r'[.!?]+', all_text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    words = all_text.split()

    total_words = len(words)
    total_sentences = len(sentences)
    avg_sentence_length = total_words / max(total_sentences, 1)

    # count syllables (rough approximation)
    def count_syllables(word):
        word = word.lower()
        vowels = 'aeiouy'
        count = 0
        prev_vowel = False
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        return max(count, 1)

    total_syllables = sum(count_syllables(w) for w in words[:5000])  # sample
    sample_words = min(len(words), 5000)
    avg_syllables = total_syllables / max(sample_words, 1)

    # Flesch Reading Ease (approximate)
    # 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
    flesch = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables

    # jargon density (chemistry-specific terms)
    jargon_terms = ['orbital', 'ligand', 'oxidation', 'coordination', 'crystal',
                    'electron', 'bonding', 'symmetry', 'spectroscopy', 'thermodynamic',
                    'kinetic', 'equilibrium', 'catalyst', 'isomer', 'polymer']
    text_lower = all_text.lower()
    jargon_count = sum(text_lower.count(term) for term in jargon_terms)
    jargon_density = jargon_count / max(total_words, 1) * 1000  # per 1000 words

    return {
        "total_words_sampled": total_words,
        "total_sentences": total_sentences,
        "avg_sentence_length": round(avg_sentence_length, 1),
        "avg_syllables_per_word": round(avg_syllables, 2),
        "flesch_reading_ease": round(flesch, 1),
        "flesch_interpretation": (
            "very easy" if flesch > 80 else
            "easy" if flesch > 70 else
            "fairly easy" if flesch > 60 else
            "standard" if flesch > 50 else
            "fairly difficult" if flesch > 30 else
            "difficult"
        ),
        "jargon_density_per_1000": round(jargon_density, 1)
    }


def main():
    print("=" * 60)
    print("TEXTBOOK STYLE ANALYSIS")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # get books
    books = get_books()
    print(f"Found {len(books)} textbooks with substantial content:")
    for book, chunks in sorted(books.items(), key=lambda x: -len(x[1])):
        print(f"  {len(chunks):5d} chunks | {book}")
    print()

    results = {}

    for book_name, all_chunks in books.items():
        print(f"\n{'=' * 60}")
        print(f"ANALYZING: {book_name}")
        print(f"{'=' * 60}")

        # sample chunks
        chunks = sample_chunks(all_chunks)
        print(f"Sampled {len(chunks)} chunks for analysis")

        book_analysis = {
            "book_name": book_name,
            "total_chunks": len(all_chunks),
            "analyzed_at": datetime.now().isoformat(),
        }

        # 1. pedagogy
        print("  [1/9] Analyzing pedagogy...")
        book_analysis["pedagogy"] = analyze_pedagogy(book_name, chunks)

        # 2. presentation style
        print("  [2/9] Analyzing presentation style...")
        book_analysis["presentation_style"] = analyze_presentation_style(book_name, chunks)

        # 3. strengths/weaknesses
        print("  [3/9] Analyzing strengths & weaknesses...")
        book_analysis["strengths_weaknesses"] = analyze_strengths_weaknesses(book_name, chunks)

        # 4. visual elements
        print("  [4/9] Analyzing visual elements...")
        book_analysis["visual_elements"] = analyze_visual_elements(book_name, chunks)

        # 5. explanation depth (WHY vs WHAT)
        print("  [5/9] Analyzing explanation depth...")
        book_analysis["explanation_depth"] = analyze_explanation_depth(book_name, chunks)

        # 6. problem-solving pedagogy
        print("  [6/9] Analyzing problem-solving approach...")
        book_analysis["problem_solving"] = analyze_problem_solving(book_name, chunks)

        # 7. real-world connections
        print("  [7/9] Analyzing real-world connections...")
        book_analysis["real_world"] = analyze_real_world_connections(book_name, chunks)

        # 8. historical context
        print("  [8/9] Analyzing historical context...")
        book_analysis["historical"] = analyze_historical_context(book_name, chunks)

        # 9. readability metrics (quantitative)
        print("  [9/9] Computing readability metrics...")
        book_analysis["readability"] = compute_readability_metrics(all_chunks[:100])

        results[book_name] = book_analysis

        # print summary
        print(f"\n  Summary for {book_name}:")
        if "teaching_philosophy" in book_analysis.get("pedagogy", {}):
            print(f"    Philosophy: {book_analysis['pedagogy'].get('teaching_philosophy', 'N/A')[:60]}")
        if "writing_tone" in book_analysis.get("presentation_style", {}):
            print(f"    Tone: {book_analysis['presentation_style'].get('writing_tone', 'N/A')}")
        if "explanation_type" in book_analysis.get("explanation_depth", {}):
            print(f"    Depth: {book_analysis['explanation_depth'].get('explanation_type', 'N/A')}")
        if "flesch_reading_ease" in book_analysis.get("readability", {}):
            print(f"    Readability: {book_analysis['readability'].get('flesch_interpretation', 'N/A')} (Flesch: {book_analysis['readability'].get('flesch_reading_ease', 'N/A')})")
        if "overall_rating" in book_analysis.get("strengths_weaknesses", {}):
            print(f"    Rating: {book_analysis['strengths_weaknesses'].get('overall_rating', 'N/A')}/10")

    # save results
    output_file = OUTPUT_DIR / "textbook_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'=' * 60}")
    print("ANALYSIS COMPLETE")
    print(f"{'=' * 60}")
    print(f"Results saved to: {output_file}")
    print(f"Analyzed {len(results)} textbooks")

    # print comparison table
    print(f"\n{'=' * 60}")
    print("COMPARISON SUMMARY")
    print(f"{'=' * 60}")
    print(f"{'Book':<35} {'Chunks':>7} {'Difficulty':<15} {'Tone':<20}")
    print("-" * 80)
    for book, analysis in sorted(results.items(), key=lambda x: -x[1]['total_chunks']):
        difficulty = analysis.get('pedagogy', {}).get('difficulty_level', 'N/A')
        tone = analysis.get('presentation_style', {}).get('writing_tone', 'N/A')
        print(f"{book[:34]:<35} {analysis['total_chunks']:>7} {str(difficulty):<15} {str(tone)[:19]:<20}")


if __name__ == "__main__":
    main()
