#!/usr/bin/env python3
"""
Lecture and Q&A Generator

Generates full prose lectures and 20+ questions per session
using the meta-book structure and RAG system.

Usage:
    python lecture_qa_generator.py --session 1
    python lecture_qa_generator.py --all
    python lecture_qa_generator.py --unit 1
"""

import json
import argparse
import urllib.request
from pathlib import Path
from typing import Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

# config
QDRANT_URL = "http://localhost:6333"
COLLECTION = "textbooks_chunks"
OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen3:latest"

BASE_DIR = Path(__file__).parent.parent
META_BOOK_FILE = BASE_DIR / "data" / "meta_book.json"
LECTURES_DIR = BASE_DIR / "lectures" / "generated"
QUIZZES_DIR = BASE_DIR / "data" / "quizzes" / "generated"

# source pdf mapping
SOURCE_PDF_MAP = {
    "atkins": "Inorganic_Chemistry_Atkins_Shriver.pdf",
    "housecroft": "ic_tina.pdf",
    "douglas": "descriptive_ic.pdf",
    "house": "descriptive_ic_house.pdf",
    "lee": "concise_ic_jd_lee.pdf",
    "basset": "ic_basset.pdf",
    "advanced": "advancex_ic_applicaionts.pdf"
}


class LectureQAGenerator:
    """
    generates lectures and Q&A from meta-book using RAG
    """

    def __init__(self):
        self.qdrant = QdrantClient(url=QDRANT_URL)
        self.meta_book = self._load_meta_book()

        # ensure output directories exist
        LECTURES_DIR.mkdir(parents=True, exist_ok=True)
        QUIZZES_DIR.mkdir(parents=True, exist_ok=True)

    def _load_meta_book(self) -> dict:
        """load meta-book configuration"""
        with open(META_BOOK_FILE) as f:
            return json.load(f)

    def _call_ollama(self, prompt: str, system: str = "") -> str:
        """call ollama API"""
        data = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
        if system:
            data["system"] = system

        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/generate",
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                result = json.loads(resp.read().decode())
                return result.get("response", "")
        except Exception as e:
            print(f"Ollama error: {e}")
            return ""

    def _query_qdrant(self, concepts: list, source_keys: list, limit: int = 20) -> list:
        """
        query qdrant for chunks matching concepts from specified sources
        """
        # map source keys to PDF names
        pdf_names = [SOURCE_PDF_MAP.get(k.lower()) for k in source_keys if k.lower() in SOURCE_PDF_MAP]

        if not pdf_names:
            print(f"  Warning: no valid sources found for {source_keys}")
            return []

        # build query text from concepts
        query_text = " ".join(concepts)

        # search with source filter
        results = []
        for pdf_name in pdf_names:
            try:
                hits = self.qdrant.query_points(
                    collection_name=COLLECTION,
                    query=query_text,
                    query_filter=Filter(
                        must=[
                            FieldCondition(
                                key="source",
                                match=MatchValue(value=pdf_name)
                            )
                        ]
                    ),
                    limit=limit // len(pdf_names) + 1,
                    with_payload=True
                )
                for hit in hits.points:
                    results.append({
                        "source": pdf_name,
                        "text": hit.payload.get("text", ""),
                        "score": hit.score
                    })
            except Exception as e:
                print(f"  Query error for {pdf_name}: {e}")

        # sort by score and return
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:limit]

    def _get_session_info(self, session_num: int) -> Optional[dict]:
        """find session info in meta-book"""
        for unit_key in ["unit_1_main_group", "unit_2_coordination", "unit_3_solid_state"]:
            if unit_key not in self.meta_book:
                continue
            for session in self.meta_book[unit_key].get("sessions", []):
                if session.get("session") == session_num:
                    return {
                        "session": session,
                        "unit": unit_key,
                        "primary_source": self.meta_book[unit_key].get("primary_source"),
                        "secondary_sources": self.meta_book[unit_key].get("secondary_sources", [])
                    }
        return None

    def generate_lecture(self, session_num: int) -> str:
        """
        generate full prose lecture for a session
        """
        info = self._get_session_info(session_num)
        if not info:
            print(f"Session {session_num} not found in meta-book")
            return ""

        session = info["session"]
        topic = session.get("topic", "")
        key_concepts = session.get("key_concepts", [])
        learning_objectives = session.get("learning_objectives", [])
        sources = session.get("sources", {})

        print(f"\nGenerating lecture for Session {session_num}: {topic}")

        # gather source keys
        source_keys = list(set([
            info["primary_source"],
            *info["secondary_sources"],
            *[v.split()[0] for v in sources.values() if isinstance(v, str)]
        ]))
        source_keys = [s for s in source_keys if s]

        print(f"  Sources: {source_keys}")
        print(f"  Concepts: {key_concepts}")

        # query RAG for relevant chunks
        chunks = self._query_qdrant(key_concepts, source_keys, limit=25)
        print(f"  Retrieved {len(chunks)} chunks")

        if not chunks:
            print("  Warning: no chunks retrieved, generating from concepts only")
            context = ""
        else:
            context = "\n\n---\n\n".join([
                f"[Source: {c['source']}]\n{c['text'][:1500]}"
                for c in chunks[:15]
            ])

        # generate lecture
        system_prompt = """You are an expert inorganic chemistry professor writing lecture notes.
Write in a clear, educational style suitable for undergraduate students.
Use proper chemical notation and terminology.
Include relevant equations and examples.
Structure the content logically with clear transitions between topics."""

        prompt = f"""Write a comprehensive lecture on the topic: {topic}

Key concepts to cover:
{chr(10).join(f"- {c}" for c in key_concepts)}

Learning objectives (students should be able to):
{chr(10).join(f"- {lo}" for lo in learning_objectives)}

Reference material from textbooks:
{context}

Write a full prose lecture (approximately 1500-2500 words) that:
1. Introduces the topic and its importance in inorganic chemistry
2. Explains each key concept clearly with examples
3. Includes relevant chemical equations and structures
4. Connects to prior knowledge and builds toward the learning objectives
5. Concludes with a summary and preview of related topics

Use markdown formatting with ## headers for major sections."""

        lecture = self._call_ollama(prompt, system_prompt)

        # add metadata header
        full_lecture = f"""# Session {session_num}: {topic}

**Scale:** {session.get('scale', 'N/A')}
**Sources:** {', '.join(source_keys)}

## Learning Objectives

{chr(10).join(f"- {lo}" for lo in learning_objectives)}

---

{lecture}

---

*Generated from meta-book synthesis of {len(source_keys)} textbook sources.*
"""

        # save lecture
        output_file = LECTURES_DIR / f"session_{session_num:02d}.md"
        with open(output_file, "w") as f:
            f.write(full_lecture)
        print(f"  Saved: {output_file}")

        return full_lecture

    def generate_qa(self, session_num: int, num_questions: int = 25) -> list:
        """
        generate Q&A questions for a session
        """
        info = self._get_session_info(session_num)
        if not info:
            print(f"Session {session_num} not found in meta-book")
            return []

        session = info["session"]
        topic = session.get("topic", "")
        key_concepts = session.get("key_concepts", [])
        learning_objectives = session.get("learning_objectives", [])
        sources = session.get("sources", {})

        print(f"\nGenerating Q&A for Session {session_num}: {topic}")

        # gather source keys
        source_keys = list(set([
            info["primary_source"],
            *info["secondary_sources"],
            *[v.split()[0] for v in sources.values() if isinstance(v, str)]
        ]))
        source_keys = [s for s in source_keys if s]

        # query RAG for relevant chunks
        chunks = self._query_qdrant(key_concepts, source_keys, limit=30)
        print(f"  Retrieved {len(chunks)} chunks")

        context = "\n\n---\n\n".join([
            f"[Source: {c['source']}]\n{c['text'][:1200]}"
            for c in chunks[:20]
        ])

        # generate questions in batches
        all_questions = []

        difficulty_specs = [
            ("recall", 8, "Basic recall and definition questions"),
            ("application", 10, "Application and calculation questions"),
            ("analysis", 7, "Analysis, comparison, and synthesis questions")
        ]

        for difficulty, count, description in difficulty_specs:
            print(f"  Generating {count} {difficulty} questions...")

            system_prompt = """You are an expert chemistry educator creating exam questions.
Generate questions that test genuine understanding, not just memorization.
Include detailed explanations for each answer.
Use proper chemical notation."""

            prompt = f"""Topic: {topic}

Key concepts: {', '.join(key_concepts)}

Learning objectives:
{chr(10).join(f"- {lo}" for lo in learning_objectives)}

Reference material:
{context}

Generate exactly {count} {description} for this topic.

For each question, provide:
1. The question text
2. Four multiple choice options (A, B, C, D)
3. The correct answer
4. A detailed explanation (2-3 sentences)
5. The specific concept being tested

Format as JSON array:
[
  {{
    "question": "...",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "answer": "A) ...",
    "explanation": "...",
    "concept": "...",
    "difficulty": "{difficulty}"
  }}
]

Generate exactly {count} questions. Output only valid JSON."""

            response = self._call_ollama(prompt, system_prompt)

            # parse JSON from response
            try:
                # find JSON array in response
                start = response.find("[")
                end = response.rfind("]") + 1
                if start >= 0 and end > start:
                    questions = json.loads(response[start:end])
                    for q in questions:
                        q["topic"] = topic
                        q["session"] = session_num
                        q["module"] = f"session_{session_num:02d}"
                    all_questions.extend(questions)
                    print(f"    Parsed {len(questions)} questions")
            except json.JSONDecodeError as e:
                print(f"    JSON parse error: {e}")

        print(f"  Total questions generated: {len(all_questions)}")

        # save questions
        output_file = QUIZZES_DIR / f"session_{session_num:02d}.json"
        with open(output_file, "w") as f:
            json.dump(all_questions, f, indent=2)
        print(f"  Saved: {output_file}")

        return all_questions

    def generate_session(self, session_num: int):
        """generate both lecture and Q&A for a session"""
        self.generate_lecture(session_num)
        self.generate_qa(session_num)

    def generate_unit(self, unit_num: int):
        """generate all sessions for a unit"""
        unit_keys = {
            1: "unit_1_main_group",
            2: "unit_2_coordination",
            3: "unit_3_solid_state"
        }
        unit_key = unit_keys.get(unit_num)
        if not unit_key or unit_key not in self.meta_book:
            print(f"Unit {unit_num} not found")
            return

        sessions = self.meta_book[unit_key].get("sessions", [])
        print(f"\nGenerating Unit {unit_num}: {len(sessions)} sessions")

        for session in sessions:
            self.generate_session(session["session"])

    def generate_all(self):
        """generate lectures and Q&A for all sessions"""
        for unit_num in [1, 2, 3]:
            self.generate_unit(unit_num)


def main():
    parser = argparse.ArgumentParser(description="Generate lectures and Q&A from meta-book")
    parser.add_argument("--session", type=int, help="Generate for specific session number")
    parser.add_argument("--unit", type=int, help="Generate for specific unit (1, 2, or 3)")
    parser.add_argument("--all", action="store_true", help="Generate for all sessions")
    parser.add_argument("--lecture-only", action="store_true", help="Generate only lectures")
    parser.add_argument("--qa-only", action="store_true", help="Generate only Q&A")

    args = parser.parse_args()

    generator = LectureQAGenerator()

    if args.session:
        if args.lecture_only:
            generator.generate_lecture(args.session)
        elif args.qa_only:
            generator.generate_qa(args.session)
        else:
            generator.generate_session(args.session)
    elif args.unit:
        generator.generate_unit(args.unit)
    elif args.all:
        generator.generate_all()
    else:
        parser.print_help()
        print("\nExample usage:")
        print("  python lecture_qa_generator.py --session 1")
        print("  python lecture_qa_generator.py --unit 1")
        print("  python lecture_qa_generator.py --all")


if __name__ == "__main__":
    main()
