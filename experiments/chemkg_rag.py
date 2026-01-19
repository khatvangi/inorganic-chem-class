#!/usr/bin/env python3
"""
ChemKG-RAG: Hybrid Knowledge Graph RAG for Inorganic Chemistry

Combines:
- KAG: Mutual indexing (chunk <-> node bidirectional linking)
- HippoRAG: PageRank on prerequisite graph
- LAG: Sub-question decomposition with dependency DAG
- LightRAG: Dual-level retrieval (concept + topic)

Excludes (v2): MMGraphRAG multimodal support
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from typing import Optional
import urllib.request

from qdrant_client import QdrantClient

# config
QDRANT_URL = "http://localhost:6333"
COLLECTION = "textbooks_chunks"
OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen3:latest"

DATA_DIR = Path(__file__).parent / "results"
GRAPH_FILE = DATA_DIR / "knowledge_graph.json"
RESULTS_FILE = DATA_DIR / "full_extraction_results.json"
ENHANCED_GRAPH_FILE = DATA_DIR / "chemkg_enhanced.json"


class ChemKGRAG:
    """
    hybrid knowledge graph RAG for inorganic chemistry
    """

    def __init__(self):
        self.qdrant = QdrantClient(url=QDRANT_URL)
        self.graph = None
        self.node_to_chunks = {}  # mutual indexing: node_id -> [chunk_ids]
        self.chunk_to_nodes = {}  # mutual indexing: chunk_id -> [node_ids]
        self.prereq_matrix = None  # for PageRank
        self.node_index = {}  # node_id -> index for matrix ops

    # =========================================================================
    # COMPONENT 1: KAG - Mutual Indexing
    # =========================================================================

    def build_mutual_index(self):
        """
        build bidirectional chunk <-> node mapping from extraction results
        this is the foundation for all other operations
        """
        print("Building mutual index (KAG)...")

        # load extraction results (has chunk_id -> extraction mapping)
        with open(RESULTS_FILE) as f:
            results = json.load(f)

        # load current graph
        with open(GRAPH_FILE) as f:
            self.graph = json.load(f)

        # build node lookup
        node_ids = {n["id"] for n in self.graph["nodes"]}

        # build bidirectional mappings
        self.node_to_chunks = defaultdict(list)
        self.chunk_to_nodes = defaultdict(list)

        for r in results:
            chunk_id = r["chunk_id"]
            norm = r.get("extraction_normalized", {})

            # link to topic
            topic = norm.get("topic")
            if topic and topic in node_ids:
                self.node_to_chunks[topic].append(chunk_id)
                self.chunk_to_nodes[chunk_id].append(topic)

            # link to concepts
            for concept in norm.get("key_concepts", []):
                if concept in node_ids:
                    self.node_to_chunks[concept].append(chunk_id)
                    self.chunk_to_nodes[chunk_id].append(concept)

            # link to prerequisites (they're also nodes)
            for prereq in norm.get("prerequisites", []):
                if prereq in node_ids:
                    self.node_to_chunks[prereq].append(chunk_id)
                    self.chunk_to_nodes[chunk_id].append(prereq)

        # add chunk_ids to graph nodes
        for node in self.graph["nodes"]:
            node["chunk_ids"] = self.node_to_chunks.get(node["id"], [])

        print(f"  Indexed {len(self.node_to_chunks)} nodes -> chunks")
        print(f"  Indexed {len(self.chunk_to_nodes)} chunks -> nodes")

        # stats
        chunks_per_node = [len(v) for v in self.node_to_chunks.values()]
        if chunks_per_node:
            print(f"  Avg chunks per node: {np.mean(chunks_per_node):.1f}")
            print(f"  Max chunks per node: {max(chunks_per_node)}")

        return self

    def get_chunks_for_node(self, node_id: str) -> list:
        """get all chunk IDs associated with a node"""
        return self.node_to_chunks.get(node_id, [])

    def get_nodes_for_chunk(self, chunk_id: str) -> list:
        """get all node IDs associated with a chunk"""
        return self.chunk_to_nodes.get(chunk_id, [])

    def retrieve_chunks(self, chunk_ids: list, limit: int = 10) -> list:
        """retrieve actual chunk content from Qdrant"""
        if not chunk_ids:
            return []

        # qdrant retrieve by IDs
        points = self.qdrant.retrieve(
            collection_name=COLLECTION,
            ids=chunk_ids[:limit],
            with_payload=True
        )

        return [{
            "id": p.id,
            "text": p.payload.get("text", ""),
            "book": p.payload.get("pdf_name", "unknown"),
            "chunk_idx": p.payload.get("chunk_idx", 0)
        } for p in points]

    # =========================================================================
    # COMPONENT 2: HippoRAG - PageRank on Prerequisites
    # =========================================================================

    def build_prereq_graph(self):
        """
        build adjacency matrix for prerequisite relationships
        enables PageRank-based importance scoring
        """
        print("Building prerequisite graph (HippoRAG)...")

        if self.graph is None:
            with open(GRAPH_FILE) as f:
                self.graph = json.load(f)

        # get all topic nodes
        topics = [n for n in self.graph["nodes"] if n["type"] == "topic"]
        self.node_index = {n["id"]: i for i, n in enumerate(topics)}
        n = len(topics)

        print(f"  Topic nodes: {n}")

        # build adjacency matrix (prerequisite_for edges)
        # if A is prerequisite_for B, then A -> B in the graph
        adj = np.zeros((n, n))

        prereq_edges = [e for e in self.graph["edges"] if e["relation"] == "prerequisite_for"]
        leads_to_edges = [e for e in self.graph["edges"] if e["relation"] == "leads_to"]

        for e in prereq_edges:
            src, tgt = e["source"], e["target"]
            if src in self.node_index and tgt in self.node_index:
                i, j = self.node_index[src], self.node_index[tgt]
                adj[i, j] = e.get("weight", 1)

        for e in leads_to_edges:
            src, tgt = e["source"], e["target"]
            if src in self.node_index and tgt in self.node_index:
                i, j = self.node_index[src], self.node_index[tgt]
                adj[i, j] = e.get("weight", 1)

        print(f"  Prerequisite edges: {len(prereq_edges)}")
        print(f"  Leads-to edges: {len(leads_to_edges)}")

        self.prereq_matrix = adj
        return self

    def pagerank(self, damping: float = 0.85, max_iter: int = 100, tol: float = 1e-6) -> dict:
        """
        compute PageRank scores for topic nodes
        higher score = more fundamental/central concept
        """
        if self.prereq_matrix is None:
            self.build_prereq_graph()

        n = self.prereq_matrix.shape[0]
        if n == 0:
            return {}

        # normalize adjacency matrix (column-stochastic)
        col_sums = self.prereq_matrix.sum(axis=0)
        col_sums[col_sums == 0] = 1  # avoid division by zero
        M = self.prereq_matrix / col_sums

        # initialize PageRank vector
        pr = np.ones(n) / n

        # power iteration
        for _ in range(max_iter):
            pr_new = (1 - damping) / n + damping * M @ pr
            if np.abs(pr_new - pr).sum() < tol:
                break
            pr = pr_new

        # map back to node IDs
        index_to_node = {i: nid for nid, i in self.node_index.items()}
        scores = {index_to_node[i]: float(pr[i]) for i in range(n)}

        return scores

    def get_prerequisites_ranked(self, topic: str, depth: int = 2) -> list:
        """
        get prerequisites for a topic, ranked by PageRank importance
        uses BFS up to specified depth, then ranks by centrality
        """
        if self.graph is None:
            with open(GRAPH_FILE) as f:
                self.graph = json.load(f)

        # build reverse edge lookup (what are prerequisites FOR this topic)
        prereq_of = defaultdict(list)
        for e in self.graph["edges"]:
            if e["relation"] == "prerequisite_for":
                prereq_of[e["target"]].append((e["source"], e.get("weight", 1)))

        # BFS to find all prerequisites up to depth
        visited = set()
        current = {topic}
        all_prereqs = []

        for d in range(depth):
            next_level = set()
            for t in current:
                for prereq, weight in prereq_of.get(t, []):
                    if prereq not in visited:
                        visited.add(prereq)
                        next_level.add(prereq)
                        all_prereqs.append({"topic": prereq, "depth": d + 1, "weight": weight})
            current = next_level

        # get PageRank scores
        pr_scores = self.pagerank()

        # rank by PageRank (higher = more fundamental)
        for p in all_prereqs:
            p["pagerank"] = pr_scores.get(p["topic"], 0)

        all_prereqs.sort(key=lambda x: -x["pagerank"])

        return all_prereqs

    # =========================================================================
    # COMPONENT 3: LAG - Sub-question Decomposition
    # =========================================================================

    def decompose_question(self, question: str) -> list:
        """
        decompose a complex question into atomic sub-questions
        returns list of sub-questions with dependencies
        """
        prompt = f"""Decompose this chemistry question into simpler sub-questions that must be answered first.

QUESTION: {question}

Rules:
1. Each sub-question should be answerable independently
2. Order them by dependency (answer earlier ones first)
3. Keep sub-questions focused on ONE concept each
4. Maximum 5 sub-questions

Return JSON:
{{
    "sub_questions": [
        {{"id": 1, "question": "...", "depends_on": []}},
        {{"id": 2, "question": "...", "depends_on": [1]}},
        ...
    ],
    "final_synthesis": "how to combine answers"
}}

/no_think"""

        result = self._query_llm(prompt)
        return result.get("sub_questions", [{"id": 1, "question": question, "depends_on": []}])

    def build_dependency_dag(self, sub_questions: list) -> list:
        """
        topological sort of sub-questions based on dependencies
        returns ordered list for sequential answering
        """
        # build adjacency list
        deps = {sq["id"]: sq.get("depends_on", []) for sq in sub_questions}
        sq_map = {sq["id"]: sq for sq in sub_questions}

        # kahn's algorithm for topological sort
        in_degree = {sid: len(d) for sid, d in deps.items()}
        queue = [sid for sid, deg in in_degree.items() if deg == 0]
        result = []

        while queue:
            sid = queue.pop(0)
            result.append(sq_map[sid])

            # reduce in-degree for dependents
            for other_id, other_deps in deps.items():
                if sid in other_deps:
                    in_degree[other_id] -= 1
                    if in_degree[other_id] == 0:
                        queue.append(other_id)

        return result

    # =========================================================================
    # COMPONENT 4: LightRAG - Dual-Level Retrieval
    # =========================================================================

    def dual_level_retrieve(self, query: str, top_k: int = 5) -> dict:
        """
        retrieve at two levels:
        1. Topic level: find relevant topics in knowledge graph
        2. Concept level: find specific concepts within topics

        returns both levels for comprehensive context
        """
        # level 1: topic retrieval via vector search
        # first embed the query using ollama
        embed_url = f"{OLLAMA_URL}/api/embed"
        embed_data = json.dumps({
            "model": "nomic-embed-text:latest",
            "input": query
        }).encode('utf-8')

        try:
            embed_req = urllib.request.Request(embed_url, data=embed_data,
                                               headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(embed_req, timeout=30) as resp:
                embed_result = json.loads(resp.read().decode('utf-8'))
                query_vector = embed_result['embeddings'][0]
        except Exception as e:
            print(f"  Embedding error: {e}")
            return {"topics": [], "concepts": [], "query": query}

        # search Qdrant with the embedding (using named vector 'dense')
        response = self.qdrant.query_points(
            collection_name=COLLECTION,
            query=query_vector,
            using="dense",  # named vector in this collection
            limit=top_k * 2,  # get more, then filter
            with_payload=True
        )
        topic_results = response.points

        # extract topics from search results
        topic_hits = defaultdict(lambda: {"score": 0, "chunks": []})
        for hit in topic_results:
            chunk_id = hit.id
            nodes = self.get_nodes_for_chunk(chunk_id)
            for node in nodes:
                # check if it's a topic node
                node_data = next((n for n in self.graph["nodes"] if n["id"] == node), None)
                if node_data and node_data.get("type") == "topic":
                    topic_hits[node]["score"] = max(topic_hits[node]["score"], hit.score)
                    topic_hits[node]["chunks"].append(chunk_id)

        # level 2: concept retrieval from top topics
        top_topics = sorted(topic_hits.items(), key=lambda x: -x[1]["score"])[:top_k]

        concept_hits = []
        for topic, data in top_topics:
            # find concepts associated with this topic
            for edge in self.graph["edges"]:
                if edge["source"] == topic and edge["relation"] == "contains":
                    concept_hits.append({
                        "concept": edge["target"],
                        "topic": topic,
                        "weight": edge.get("weight", 1)
                    })

        return {
            "topics": [{"topic": t, **d} for t, d in top_topics],
            "concepts": concept_hits[:top_k * 3],
            "query": query
        }

    # =========================================================================
    # UNIFIED QUERY INTERFACE
    # =========================================================================

    def answer_question(self, question: str, verbose: bool = True) -> dict:
        """
        full ChemKG-RAG pipeline:
        1. LAG: decompose question
        2. LAG: build dependency DAG
        3. for each sub-question:
           - LightRAG: dual-level retrieval
           - HippoRAG: get ranked prerequisites
           - KAG: retrieve source chunks
           - generate answer
        4. synthesize final answer
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"ChemKG-RAG Query: {question[:50]}...")
            print("="*60)

        # step 1: decompose (LAG)
        if verbose:
            print("\n[1/4] Decomposing question (LAG)...")
        sub_questions = self.decompose_question(question)
        ordered_sqs = self.build_dependency_dag(sub_questions)

        if verbose:
            print(f"  Sub-questions: {len(ordered_sqs)}")
            for sq in ordered_sqs:
                print(f"    {sq['id']}. {sq['question'][:50]}...")

        # step 2-3: answer each sub-question
        answers = {}
        all_context = []

        for sq in ordered_sqs:
            sq_id = sq["id"]
            sq_text = sq["question"]

            if verbose:
                print(f"\n[2/4] Processing sub-question {sq_id}...")

            # dual-level retrieval (LightRAG)
            retrieval = self.dual_level_retrieve(sq_text)

            if verbose:
                print(f"  Topics found: {len(retrieval['topics'])}")
                print(f"  Concepts found: {len(retrieval['concepts'])}")

            # get prerequisites for top topic (HippoRAG)
            prereqs = []
            if retrieval["topics"]:
                top_topic = retrieval["topics"][0]["topic"]
                prereqs = self.get_prerequisites_ranked(top_topic, depth=2)[:5]

                if verbose:
                    print(f"  Prerequisites: {[p['topic'] for p in prereqs[:3]]}")

            # retrieve source chunks (KAG mutual indexing)
            chunk_ids = []
            for t in retrieval["topics"][:3]:
                chunk_ids.extend(t.get("chunks", []))
            chunks = self.retrieve_chunks(list(set(chunk_ids)), limit=5)

            if verbose:
                print(f"  Source chunks: {len(chunks)}")

            # build context
            context = {
                "sub_question": sq_text,
                "topics": [t["topic"] for t in retrieval["topics"]],
                "concepts": [c["concept"] for c in retrieval["concepts"][:5]],
                "prerequisites": [p["topic"] for p in prereqs],
                "chunks": [c["text"][:500] for c in chunks],
                "previous_answers": {k: answers[k][:200] for k in sq.get("depends_on", []) if k in answers}
            }
            all_context.append(context)

            # generate answer for sub-question
            answer = self._generate_answer(sq_text, context)
            answers[sq_id] = answer

            if verbose:
                print(f"  Answer: {answer[:100]}...")

        # step 4: synthesize final answer
        if verbose:
            print(f"\n[4/4] Synthesizing final answer...")

        final_answer = self._synthesize_answers(question, answers, all_context)

        result = {
            "question": question,
            "sub_questions": ordered_sqs,
            "sub_answers": answers,
            "final_answer": final_answer,
            "context_used": all_context
        }

        if verbose:
            print(f"\n{'='*60}")
            print("FINAL ANSWER:")
            print("="*60)
            print(final_answer)

        return result

    # =========================================================================
    # LLM HELPERS
    # =========================================================================

    def _query_llm(self, prompt: str, temperature: float = 0.1) -> dict:
        """query Qwen3 with JSON output"""
        url = f"{OLLAMA_URL}/api/generate"
        data = json.dumps({
            "model": MODEL,
            "prompt": prompt,
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

    def _generate_answer(self, question: str, context: dict) -> str:
        """generate answer for a sub-question using context"""
        chunks_text = "\n---\n".join(context.get("chunks", []))
        prereqs = ", ".join(context.get("prerequisites", []))
        prev_answers = "\n".join([f"Q{k}: {v}" for k, v in context.get("previous_answers", {}).items()])

        prompt = f"""Answer this chemistry question using the provided context.

QUESTION: {question}

RELEVANT TOPICS: {', '.join(context.get('topics', []))}
KEY CONCEPTS: {', '.join(context.get('concepts', []))}
PREREQUISITES TO CONSIDER: {prereqs}

TEXTBOOK EXCERPTS:
{chunks_text[:2000]}

{f'PREVIOUS ANSWERS:{chr(10)}{prev_answers}' if prev_answers else ''}

Provide a clear, accurate answer focused on the chemistry. Be concise but complete.
Do NOT include any <think> tags or reasoning process - just the answer.

/no_think"""

        url = f"{OLLAMA_URL}/api/generate"
        data = json.dumps({
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3}
        }).encode('utf-8')

        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('response', 'Error generating answer')
        except Exception as e:
            return f"Error: {str(e)}"

    def _synthesize_answers(self, question: str, answers: dict, context: list) -> str:
        """synthesize sub-answers into final comprehensive answer"""
        answers_text = "\n\n".join([f"Part {k}: {v}" for k, v in sorted(answers.items())])

        prompt = f"""Synthesize these partial answers into a complete, coherent response.

ORIGINAL QUESTION: {question}

PARTIAL ANSWERS:
{answers_text}

Combine these into a single, well-structured answer that:
1. Directly addresses the original question
2. Maintains logical flow
3. Removes redundancy
4. Is accurate and complete

Do NOT include any <think> tags or reasoning process - just the answer.

/no_think"""

        url = f"{OLLAMA_URL}/api/generate"
        data = json.dumps({
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3}
        }).encode('utf-8')

        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('response', answers_text)
        except Exception as e:
            return answers_text  # fallback to concatenated answers

    # =========================================================================
    # COMPONENT 5: GraphRAG - Cross-Book Community Detection
    # =========================================================================

    def detect_communities(self, resolution: float = 1.0) -> dict:
        """
        detect topic communities using connected components + label propagation
        fast O(E) algorithm instead of O(n^3) modularity
        """
        print("Detecting topic communities (GraphRAG)...")

        if self.graph is None:
            with open(GRAPH_FILE) as f:
                self.graph = json.load(f)

        # build adjacency for topics only
        topics = {n["id"]: n for n in self.graph["nodes"] if n["type"] == "topic"}
        topic_list = list(topics.keys())
        topic_set = set(topic_list)

        # build adjacency list (faster than matrix for sparse graphs)
        adj = defaultdict(list)
        for e in self.graph["edges"]:
            src, tgt = e["source"], e["target"]
            if src in topic_set and tgt in topic_set:
                w = e.get("weight", 1)
                adj[src].append((tgt, w))
                adj[tgt].append((src, w))

        print(f"  Topics: {len(topics)}, Edges: {sum(len(v) for v in adj.values())//2}")

        # label propagation algorithm (fast community detection)
        labels = {t: i for i, t in enumerate(topic_list)}

        for iteration in range(10):  # typically converges in 3-5 iterations
            changed = False
            for topic in topic_list:
                if topic not in adj:
                    continue

                # count neighbor labels weighted by edge weight
                neighbor_labels = defaultdict(float)
                for neighbor, weight in adj[topic]:
                    neighbor_labels[labels[neighbor]] += weight

                if neighbor_labels:
                    # assign most common neighbor label
                    best_label = max(neighbor_labels.items(), key=lambda x: x[1])[0]
                    if labels[topic] != best_label:
                        labels[topic] = best_label
                        changed = True

            if not changed:
                print(f"  Converged after {iteration+1} iterations")
                break

        # build community structure
        comm_topics = defaultdict(list)
        for topic, label in labels.items():
            comm_topics[label].append(topic)

        # name communities by most frequent topic
        named_communities = {}
        for comm_id, topic_ids in comm_topics.items():
            if len(topic_ids) > 1:  # skip singletons
                sorted_topics = sorted(topic_ids, key=lambda t: -topics[t].get("count", 0))
                comm_name = sorted_topics[0]
                named_communities[comm_name] = {
                    "name": comm_name,
                    "topics": topic_ids,
                    "size": len(topic_ids),
                    "total_count": sum(topics[t].get("count", 0) for t in topic_ids)
                }

        print(f"  Found {len(named_communities)} communities")
        print(f"  Largest: {max(c['size'] for c in named_communities.values()) if named_communities else 0} topics")

        return named_communities

    def get_cross_book_coverage(self, topic: str) -> dict:
        """
        get coverage of a topic across different textbooks
        useful for synthesizing multiple perspectives
        """
        if self.graph is None:
            self.load_enhanced_graph()

        # get chunks for this topic
        chunk_ids = self.node_to_chunks.get(topic, [])
        if not chunk_ids:
            return {"topic": topic, "books": {}, "total_chunks": 0}

        # retrieve chunk metadata
        chunks = self.retrieve_chunks(chunk_ids, limit=100)

        # group by book
        book_coverage = defaultdict(lambda: {"count": 0, "chunks": []})
        for c in chunks:
            book = c.get("book", "unknown")
            book_coverage[book]["count"] += 1
            book_coverage[book]["chunks"].append(c["id"])

        return {
            "topic": topic,
            "books": dict(book_coverage),
            "total_chunks": len(chunks),
            "num_books": len(book_coverage)
        }

    def synthesize_perspectives(self, topic: str, max_per_book: int = 2) -> str:
        """
        synthesize explanations of a topic from multiple textbooks
        preserves each book's unique voice while creating coherent summary
        """
        coverage = self.get_cross_book_coverage(topic)

        if coverage["total_chunks"] == 0:
            return f"No content found for topic: {topic}"

        # get sample chunks from each book
        all_excerpts = []
        for book, data in coverage["books"].items():
            chunks = self.retrieve_chunks(data["chunks"][:max_per_book])
            for c in chunks:
                all_excerpts.append(f"[{book}]:\n{c['text'][:800]}")

        excerpts_text = "\n\n---\n\n".join(all_excerpts)

        prompt = f"""Synthesize these textbook explanations of "{topic}" into a comprehensive summary.

TEXTBOOK EXCERPTS:
{excerpts_text[:3000]}

Create a synthesis that:
1. Captures key points from each textbook
2. Notes any differences in emphasis or approach
3. Provides a complete understanding of {topic}
4. Mentions which book is best for which aspect

Do NOT include any <think> tags.

/no_think"""

        url = f"{OLLAMA_URL}/api/generate"
        data = json.dumps({
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3}
        }).encode('utf-8')

        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('response', 'Error synthesizing')
        except Exception as e:
            return f"Error: {str(e)}"

    # =========================================================================
    # SAVE/LOAD ENHANCED GRAPH
    # =========================================================================

    def save_enhanced_graph(self):
        """save graph with mutual indexing to file"""
        if self.graph is None:
            print("No graph to save. Run build_mutual_index() first.")
            return

        # add PageRank scores
        pr_scores = self.pagerank()
        for node in self.graph["nodes"]:
            node["pagerank"] = pr_scores.get(node["id"], 0)

        # update metadata
        self.graph["metadata"]["mutual_indexing"] = True
        self.graph["metadata"]["pagerank_computed"] = True
        self.graph["metadata"]["enhanced_at"] = __import__("datetime").datetime.now().isoformat()

        with open(ENHANCED_GRAPH_FILE, 'w') as f:
            json.dump(self.graph, f, indent=2)

        print(f"Enhanced graph saved to {ENHANCED_GRAPH_FILE}")

    def load_enhanced_graph(self):
        """load enhanced graph if available, otherwise build it"""
        if ENHANCED_GRAPH_FILE.exists():
            with open(ENHANCED_GRAPH_FILE) as f:
                self.graph = json.load(f)

            # rebuild in-memory indices
            self.node_to_chunks = defaultdict(list)
            self.chunk_to_nodes = defaultdict(list)  # reset as defaultdict
            for node in self.graph["nodes"]:
                self.node_to_chunks[node["id"]] = node.get("chunk_ids", [])
                for cid in node.get("chunk_ids", []):
                    self.chunk_to_nodes[cid].append(node["id"])

            print(f"Loaded enhanced graph from {ENHANCED_GRAPH_FILE}")
        else:
            print("No enhanced graph found. Building...")
            self.build_mutual_index()
            self.build_prereq_graph()
            self.save_enhanced_graph()

        return self


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="ChemKG-RAG: Hybrid Knowledge Graph RAG")
    parser.add_argument("--build", action="store_true", help="Build/rebuild enhanced graph")
    parser.add_argument("--query", type=str, help="Query the system")
    parser.add_argument("--prereqs", type=str, help="Get prerequisites for a topic")
    parser.add_argument("--stats", action="store_true", help="Show graph statistics")
    parser.add_argument("--communities", action="store_true", help="Detect topic communities")
    parser.add_argument("--coverage", type=str, help="Get cross-book coverage for a topic")
    parser.add_argument("--synthesize", type=str, help="Synthesize perspectives on a topic")
    args = parser.parse_args()

    rag = ChemKGRAG()

    if args.build:
        print("Building ChemKG-RAG enhanced graph...")
        rag.build_mutual_index()
        rag.build_prereq_graph()
        rag.save_enhanced_graph()
        print("Done!")

    elif args.query:
        rag.load_enhanced_graph()
        result = rag.answer_question(args.query)
        print("\n" + "="*60)
        print("Full result saved. Final answer above.")

    elif args.prereqs:
        rag.load_enhanced_graph()
        rag.build_prereq_graph()
        prereqs = rag.get_prerequisites_ranked(args.prereqs)
        print(f"\nPrerequisites for '{args.prereqs}':")
        print("-" * 40)
        for p in prereqs[:10]:
            print(f"  {p['topic']:40} (PageRank: {p['pagerank']:.4f}, depth: {p['depth']})")

    elif args.stats:
        rag.load_enhanced_graph()
        print("\nChemKG-RAG Statistics:")
        print("-" * 40)
        print(f"  Total nodes: {len(rag.graph['nodes'])}")
        print(f"  Total edges: {len(rag.graph['edges'])}")
        print(f"  Nodes with chunks: {sum(1 for n in rag.graph['nodes'] if n.get('chunk_ids'))}")
        print(f"  Avg chunks/node: {np.mean([len(n.get('chunk_ids', [])) for n in rag.graph['nodes']]):.1f}")

        # top PageRank topics
        rag.build_prereq_graph()
        pr = rag.pagerank()
        top_pr = sorted(pr.items(), key=lambda x: -x[1])[:10]
        print("\nTop 10 topics by PageRank (most fundamental):")
        for topic, score in top_pr:
            print(f"  {topic:40} {score:.4f}")

    elif args.communities:
        rag.load_enhanced_graph()
        communities = rag.detect_communities()
        print("\nTop 10 Topic Communities:")
        print("-" * 60)
        sorted_comms = sorted(communities.values(), key=lambda x: -x["size"])[:10]
        for c in sorted_comms:
            print(f"\n{c['name']} ({c['size']} topics, {c['total_count']} mentions)")
            print(f"  Topics: {', '.join(c['topics'][:5])}{'...' if len(c['topics']) > 5 else ''}")

    elif args.coverage:
        rag.load_enhanced_graph()
        coverage = rag.get_cross_book_coverage(args.coverage)
        print(f"\nCross-Book Coverage: {coverage['topic']}")
        print("-" * 40)
        print(f"  Total chunks: {coverage['total_chunks']}")
        print(f"  Books covered: {coverage['num_books']}")
        for book, data in sorted(coverage["books"].items(), key=lambda x: -x[1]["count"]):
            print(f"    {book[:40]:40} {data['count']:3d} chunks")

    elif args.synthesize:
        rag.load_enhanced_graph()
        print(f"\nSynthesizing perspectives on: {args.synthesize}")
        print("-" * 60)
        synthesis = rag.synthesize_perspectives(args.synthesize)
        print(synthesis)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
