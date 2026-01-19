#!/usr/bin/env python3
"""
Data-Driven Curriculum Generator

Generates course sequence from knowledge graph using multiple strategies:
1. Topological Sort - respects prerequisite order
2. PageRank - fundamentals first
3. Hybrid - PageRank weighted, prerequisite constrained
4. Coverage - textbook emphasis
5. Depth-First - deep dive into branches
6. Community-Based - cluster related topics
"""

import json
from collections import defaultdict, deque
from pathlib import Path
import numpy as np

DATA_DIR = Path(__file__).parent / "results"
GRAPH_FILE = DATA_DIR / "chemkg_enhanced.json"


class CurriculumGenerator:
    def __init__(self):
        with open(GRAPH_FILE) as f:
            self.graph = json.load(f)

        self.topics = {n["id"]: n for n in self.graph["nodes"] if n["type"] == "topic"}
        self.pagerank = {n["id"]: n.get("pagerank", 0) for n in self.graph["nodes"]}

        # build adjacency
        self.adj = defaultdict(list)  # topic -> dependents
        self.reverse_adj = defaultdict(list)  # topic -> prerequisites
        self.edge_weights = {}

        for e in self.graph["edges"]:
            if e["relation"] in ["prerequisite_for", "leads_to"]:
                src, tgt = e["source"], e["target"]
                if src in self.topics and tgt in self.topics:
                    self.adj[src].append(tgt)
                    self.reverse_adj[tgt].append(src)
                    self.edge_weights[(src, tgt)] = e.get("weight", 1)

    def filter_significant(self, topic_list, min_count=10):
        """filter to topics with minimum mention count"""
        return [t for t in topic_list if self.topics[t].get("count", 0) >= min_count]

    # =========================================================================
    # METHOD 1: TOPOLOGICAL SORT
    # =========================================================================
    def topological_sort(self, min_count=10):
        """
        Kahn's algorithm - respects prerequisites
        among equal candidates, picks by mention count
        """
        in_degree = defaultdict(int)
        for src in self.adj:
            for tgt in self.adj[src]:
                in_degree[tgt] += 1

        queue = [t for t in self.topics if in_degree[t] == 0]
        result = []

        while queue:
            # sort by count (most mentioned first)
            queue.sort(key=lambda t: -self.topics[t].get("count", 0))
            node = queue.pop(0)
            result.append(node)

            for neighbor in self.adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return self.filter_significant(result, min_count)

    # =========================================================================
    # METHOD 2: PAGERANK ORDER
    # =========================================================================
    def pagerank_order(self, min_count=10):
        """
        order by PageRank score - most fundamental first
        ignores prerequisite constraints
        """
        significant = [t for t in self.topics if self.topics[t].get("count", 0) >= min_count]
        return sorted(significant, key=lambda t: -self.pagerank.get(t, 0))

    # =========================================================================
    # METHOD 3: HYBRID (PageRank + Prerequisites)
    # =========================================================================
    def hybrid_order(self, min_count=10):
        """
        greedy selection: pick highest PageRank among topics
        whose prerequisites are already satisfied
        """
        satisfied = set()
        result = []
        remaining = set(t for t in self.topics if self.topics[t].get("count", 0) >= min_count)

        while remaining:
            # find ready topics (all prereqs satisfied)
            ready = []
            for t in remaining:
                prereqs = [p for p in self.reverse_adj.get(t, []) if p in remaining]
                if all(p in satisfied for p in prereqs):
                    ready.append(t)

            if not ready:
                # break cycles - pick highest PR from remaining
                ready = list(remaining)

            # pick best by PageRank
            best = max(ready, key=lambda t: self.pagerank.get(t, 0))
            result.append(best)
            satisfied.add(best)
            remaining.remove(best)

        return result

    # =========================================================================
    # METHOD 4: COVERAGE ORDER
    # =========================================================================
    def coverage_order(self, min_count=10):
        """
        order by textbook coverage (mention count)
        topics emphasized by more textbooks come first
        """
        significant = [t for t in self.topics if self.topics[t].get("count", 0) >= min_count]
        return sorted(significant, key=lambda t: -self.topics[t].get("count", 0))

    # =========================================================================
    # METHOD 5: DEPTH-FIRST FROM CORE
    # =========================================================================
    def depth_first_order(self, min_count=10, start_topics=None):
        """
        start from core concepts, go deep into each branch
        good for "master one thing before moving on" approach
        """
        if start_topics is None:
            # start from highest PageRank topics
            start_topics = self.pagerank_order(min_count)[:5]

        visited = set()
        result = []

        def dfs(topic):
            if topic in visited:
                return
            if self.topics[topic].get("count", 0) < min_count:
                return
            visited.add(topic)
            result.append(topic)

            # visit dependents sorted by PageRank
            dependents = sorted(self.adj.get(topic, []),
                              key=lambda t: -self.pagerank.get(t, 0))
            for dep in dependents:
                dfs(dep)

        for start in start_topics:
            dfs(start)

        # add any remaining significant topics
        for t in self.topics:
            if t not in visited and self.topics[t].get("count", 0) >= min_count:
                dfs(t)

        return result

    # =========================================================================
    # METHOD 6: BREADTH-FIRST FROM CORE
    # =========================================================================
    def breadth_first_order(self, min_count=10, start_topics=None):
        """
        cover all fundamentals first, then second level, etc.
        good for building broad foundation before specializing
        """
        if start_topics is None:
            start_topics = self.pagerank_order(min_count)[:5]

        visited = set()
        result = []
        queue = deque(start_topics)

        while queue:
            topic = queue.popleft()
            if topic in visited:
                continue
            if self.topics[topic].get("count", 0) < min_count:
                continue

            visited.add(topic)
            result.append(topic)

            # add dependents to queue (sorted by PageRank)
            dependents = sorted(self.adj.get(topic, []),
                              key=lambda t: -self.pagerank.get(t, 0))
            for dep in dependents:
                if dep not in visited:
                    queue.append(dep)

        # add remaining
        for t in self.topics:
            if t not in visited and self.topics[t].get("count", 0) >= min_count:
                result.append(t)

        return result

    # =========================================================================
    # METHOD 7: COMMUNITY-BASED (cluster related topics)
    # =========================================================================
    def community_order(self, min_count=10):
        """
        group related topics together using graph communities
        teaches related concepts as units
        """
        # simple label propagation for communities
        labels = {t: i for i, t in enumerate(self.topics)}

        for _ in range(10):
            changed = False
            for topic in self.topics:
                neighbors = self.adj.get(topic, []) + self.reverse_adj.get(topic, [])
                if neighbors:
                    neighbor_labels = defaultdict(int)
                    for n in neighbors:
                        neighbor_labels[labels[n]] += 1
                    best = max(neighbor_labels.items(), key=lambda x: x[1])[0]
                    if labels[topic] != best:
                        labels[topic] = best
                        changed = True
            if not changed:
                break

        # group by community
        communities = defaultdict(list)
        for t, label in labels.items():
            if self.topics[t].get("count", 0) >= min_count:
                communities[label].append(t)

        # sort communities by total PageRank
        sorted_comms = sorted(communities.values(),
                            key=lambda c: -sum(self.pagerank.get(t, 0) for t in c))

        # within each community, sort by PageRank
        result = []
        for comm in sorted_comms:
            comm_sorted = sorted(comm, key=lambda t: -self.pagerank.get(t, 0))
            result.extend(comm_sorted)

        return result

    # =========================================================================
    # METHOD 8: DIFFICULTY-BASED (prerequisite depth)
    # =========================================================================
    def difficulty_order(self, min_count=10):
        """
        order by "difficulty" = number of prerequisites
        simpler topics first
        """
        difficulty = {}
        for t in self.topics:
            # count total prerequisites (direct + indirect via BFS)
            visited = set()
            queue = deque(self.reverse_adj.get(t, []))
            while queue:
                prereq = queue.popleft()
                if prereq not in visited:
                    visited.add(prereq)
                    queue.extend(self.reverse_adj.get(prereq, []))
            difficulty[t] = len(visited)

        significant = [t for t in self.topics if self.topics[t].get("count", 0) >= min_count]
        return sorted(significant, key=lambda t: (difficulty[t], -self.topics[t].get("count", 0)))

    # =========================================================================
    # GENERATE ALL AND COMPARE
    # =========================================================================
    def generate_all(self, min_count=10, top_n=30):
        """generate curricula using all methods"""
        methods = {
            "topological": self.topological_sort(min_count),
            "pagerank": self.pagerank_order(min_count),
            "hybrid": self.hybrid_order(min_count),
            "coverage": self.coverage_order(min_count),
            "depth_first": self.depth_first_order(min_count),
            "breadth_first": self.breadth_first_order(min_count),
            "community": self.community_order(min_count),
            "difficulty": self.difficulty_order(min_count),
        }

        return {name: order[:top_n] for name, order in methods.items()}

    def print_comparison(self, min_count=10, top_n=25):
        """print side-by-side comparison"""
        curricula = self.generate_all(min_count, top_n)

        print("\n" + "="*80)
        print("CURRICULUM COMPARISON (8 Methods)")
        print("="*80)

        for name, order in curricula.items():
            print(f"\n--- {name.upper()} ({len(order)} topics) ---")
            for i, t in enumerate(order[:15], 1):
                count = self.topics[t].get("count", 0)
                pr = self.pagerank.get(t, 0)
                print(f"  {i:2}. {t[:45]:<45} ({count:4} mentions, PR:{pr:.4f})")
            if len(order) > 15:
                print(f"  ... and {len(order)-15} more")

    def export_curriculum(self, method="hybrid", min_count=10, output_file=None):
        """export curriculum to JSON"""
        methods = {
            "topological": self.topological_sort,
            "pagerank": self.pagerank_order,
            "hybrid": self.hybrid_order,
            "coverage": self.coverage_order,
            "depth_first": self.depth_first_order,
            "breadth_first": self.breadth_first_order,
            "community": self.community_order,
            "difficulty": self.difficulty_order,
        }

        order = methods[method](min_count)

        curriculum = {
            "method": method,
            "min_count": min_count,
            "total_topics": len(order),
            "topics": []
        }

        for i, t in enumerate(order, 1):
            curriculum["topics"].append({
                "rank": i,
                "topic": t,
                "mentions": self.topics[t].get("count", 0),
                "pagerank": self.pagerank.get(t, 0),
                "prerequisites": self.reverse_adj.get(t, []),
                "leads_to": self.adj.get(t, [])
            })

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(curriculum, f, indent=2)
            print(f"Exported to {output_file}")

        return curriculum


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate data-driven curriculum")
    parser.add_argument("--method", type=str, default="all",
                       choices=["topological", "pagerank", "hybrid", "coverage",
                               "depth_first", "breadth_first", "community", "difficulty", "all"],
                       help="Ordering method")
    parser.add_argument("--min-count", type=int, default=10,
                       help="Minimum mention count for topics")
    parser.add_argument("--top", type=int, default=30,
                       help="Number of topics to show")
    parser.add_argument("--export", type=str, help="Export to JSON file")
    args = parser.parse_args()

    gen = CurriculumGenerator()

    if args.method == "all":
        gen.print_comparison(args.min_count, args.top)
    else:
        curriculum = gen.export_curriculum(args.method, args.min_count, args.export)

        print(f"\n{'='*60}")
        print(f"CURRICULUM: {args.method.upper()}")
        print(f"{'='*60}")

        for item in curriculum["topics"][:args.top]:
            print(f"  {item['rank']:2}. {item['topic'][:45]:<45} ({item['mentions']} mentions)")


if __name__ == "__main__":
    main()
