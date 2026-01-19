#!/usr/bin/env python3
"""
Path Tracer: Dynamic prerequisite path generation

given a target concept (from a question), traces back through
the knowledge graph to find all prerequisite paths.

outputs JSON suitable for visualization (funnel/graph).
"""

import json
import sys
from collections import defaultdict, deque
from pathlib import Path

# scales in order (funnel layers)
SCALE_ORDER = ['QUANTUM', 'ELECTRONIC', 'STRUCTURAL', 'DESCRIPTIVE', 'APPLICATION']
SCALE_DEPTH = {s: i for i, s in enumerate(SCALE_ORDER)}


class PathTracer:
    def __init__(self, graph_path: str):
        """load knowledge graph"""
        with open(graph_path) as f:
            self.graph = json.load(f)

        # build lookup structures
        self.nodes = {}
        for n in self.graph['nodes']:
            self.nodes[n['id']] = {
                'label': n.get('label', n['id']),
                'type': n.get('type', 'concept'),
                'count': n.get('count', 0),
                'scale': n.get('group', 'DESCRIPTIVE'),  # group often = scale
                'pagerank': n.get('pagerank', 0)
            }

        # build adjacency (reverse for tracing back)
        self.prereqs = defaultdict(list)  # concept -> its prerequisites
        self.enables = defaultdict(list)   # concept -> what it enables

        for e in self.graph['edges']:
            if e.get('relation') == 'prerequisite_for':
                target = e['target']
                source = e['source']
                self.prereqs[target].append(source)
                self.enables[source].append(target)

        print(f"Loaded graph: {len(self.nodes)} nodes, {len(self.graph['edges'])} edges")

    def find_concept(self, query: str) -> list:
        """fuzzy match query to concept names"""
        query_lower = query.lower()
        matches = []

        for cid, cdata in self.nodes.items():
            cid_lower = cid.lower()
            if query_lower in cid_lower or cid_lower in query_lower:
                matches.append((cid, cdata, len(cid)))  # shorter = better match

        # sort by length (prefer exact/short matches)
        matches.sort(key=lambda x: x[2])
        return [(m[0], m[1]) for m in matches[:5]]

    def trace_prerequisites(self, target: str, max_depth: int = 5) -> dict:
        """
        trace all prerequisite paths back from target.
        returns tree structure with depth and scale info.
        """
        if target not in self.nodes:
            return {"error": f"Concept '{target}' not found"}

        visited = set()
        result = {
            'target': target,
            'target_info': self.nodes[target],
            'paths': [],
            'all_nodes': {},
            'all_edges': [],
            'layers': defaultdict(list)  # scale -> nodes at that scale
        }

        # BFS to find all prerequisites
        queue = deque([(target, 0, [target])])  # (node, depth, path)

        while queue:
            current, depth, path = queue.popleft()

            if current in visited or depth > max_depth:
                continue
            visited.add(current)

            # add to results
            node_info = self.nodes.get(current, {'scale': 'UNKNOWN', 'count': 0})
            # infer scale from topic name since graph doesn't have it
            scale = self._infer_scale(current)

            result['all_nodes'][current] = {
                'id': current,
                'scale': scale,
                'depth': depth,
                'count': node_info.get('count', 0),
                'pagerank': node_info.get('pagerank', 0),
                'is_target': current == target
            }
            result['layers'][scale].append(current)

            # get prerequisites
            prereqs = self.prereqs.get(current, [])

            for prereq in prereqs:
                if prereq not in visited and prereq != current:  # avoid self-loops
                    result['all_edges'].append({
                        'source': prereq,
                        'target': current,
                        'depth': depth + 1
                    })
                    queue.append((prereq, depth + 1, path + [prereq]))

        # convert layers to list format
        result['layers'] = dict(result['layers'])

        # compute funnel structure (layers ordered by scale)
        result['funnel'] = []
        for scale in SCALE_ORDER:
            if scale in result['layers']:
                result['funnel'].append({
                    'scale': scale,
                    'depth': SCALE_DEPTH[scale],
                    'nodes': result['layers'][scale],
                    'count': len(result['layers'][scale])
                })

        return result

    def _normalize_scale(self, scale: str) -> str:
        """normalize scale names - infer from topic if needed"""
        scale_upper = scale.upper()
        for s in SCALE_ORDER:
            if s in scale_upper:
                return s
        return 'DESCRIPTIVE'  # default

    def _infer_scale(self, topic_name: str) -> str:
        """infer scale from topic name keywords"""
        name_lower = topic_name.lower()

        # QUANTUM indicators
        quantum_keywords = ['quantum', 'wave function', 'orbital', 'schrodinger', 'atomic structure',
                           'electron configuration', 'quantum number', 'spin', 'pauli']
        if any(kw in name_lower for kw in quantum_keywords):
            return 'QUANTUM'

        # ELECTRONIC indicators
        electronic_keywords = ['crystal field', 'molecular orbital', 'mo theory', 'bonding',
                              'electronic', 'd-orbital', 'splitting', 'cfse', 'ligand field',
                              'band', 'magnetism', 'magnetic', 'spectroscopy', 'color']
        if any(kw in name_lower for kw in electronic_keywords):
            return 'ELECTRONIC'

        # STRUCTURAL indicators
        structural_keywords = ['symmetry', 'point group', 'geometry', 'structure', 'crystal',
                              'coordination', 'isomer', 'lattice', 'unit cell', 'packing']
        if any(kw in name_lower for kw in structural_keywords):
            return 'STRUCTURAL'

        # APPLICATION indicators
        application_keywords = ['application', 'industrial', 'biological', 'catalysis', 'material',
                               'environmental', 'medicine', 'synthesis', 'reaction mechanism']
        if any(kw in name_lower for kw in application_keywords):
            return 'APPLICATION'

        # Default to DESCRIPTIVE
        return 'DESCRIPTIVE'

    def generate_learning_path(self, target: str, known: list = None) -> dict:
        """
        generate optimal learning path to target, skipping known concepts.
        returns ordered list of concepts to learn.
        """
        known = set(known or [])
        trace = self.trace_prerequisites(target)

        if 'error' in trace:
            return trace

        # topological sort of prerequisites
        all_nodes = set(trace['all_nodes'].keys())
        to_learn = all_nodes - known - {target}

        # build dependency order
        in_degree = defaultdict(int)
        for edge in trace['all_edges']:
            if edge['target'] in to_learn:
                in_degree[edge['target']] += 1

        # nodes with no prerequisites (or all prereqs known)
        queue = deque([n for n in to_learn if in_degree[n] == 0])
        order = []

        while queue:
            current = queue.popleft()
            order.append(current)

            for edge in trace['all_edges']:
                if edge['source'] == current and edge['target'] in to_learn:
                    in_degree[edge['target']] -= 1
                    if in_degree[edge['target']] == 0:
                        queue.append(edge['target'])

        # add remaining (might have cycles)
        remaining = to_learn - set(order)
        order.extend(remaining)

        # add target at end
        order.append(target)

        # build path with metadata
        path = []
        for i, concept in enumerate(order):
            node_info = trace['all_nodes'].get(concept, {})
            path.append({
                'step': i + 1,
                'concept': concept,
                'scale': node_info.get('scale', 'UNKNOWN'),
                'status': 'known' if concept in known else ('target' if concept == target else 'to_learn'),
                'pagerank': node_info.get('pagerank', 0)
            })

        return {
            'target': target,
            'total_steps': len(path),
            'new_concepts': len(to_learn),
            'path': path
        }

    def question_to_path(self, question: str) -> dict:
        """
        take a natural language question, find relevant concept,
        trace path, return visualization data.
        """
        # extract key terms (simple approach)
        key_terms = [
            'color', 'blue', 'green', 'red',  # → Color/d-d transitions
            'magnetic', 'paramagnet', 'diamagnet',  # → Magnetism
            'crystal field', 'splitting', 'CFT',  # → Crystal Field Theory
            'orbital', 'MO', 'bonding',  # → MO Theory
            'structure', 'geometry', 'shape',  # → Coordination/Structure
            'acid', 'base', 'pH',  # → Acid-Base
            'redox', 'oxidation', 'reduction',  # → Redox
            'solid', 'crystal', 'lattice',  # → Solid State
            'symmetry', 'point group',  # → Symmetry
            'periodic', 'trend',  # → Periodic Trends
        ]

        question_lower = question.lower()

        # map to concepts
        concept_map = {
            'color': 'Color And Magnetism Of Coordination Compounds',
            'blue': 'Crystal Field Theory',
            'magnetic': 'Magnetic Properties Of Transition Metals',
            'crystal field': 'Crystal Field Theory',
            'splitting': 'Crystal Field Theory',
            'orbital': 'Molecular Orbital Theory',
            'symmetry': 'Molecular Symmetry And Group Theory',
            'point group': 'Symmetry And Point Groups',
            'solid': 'Solid State Chemistry',
            'lattice': 'Crystal Structures',
            'acid': 'Acid-Base Chemistry',
            'redox': 'Redox Chemistry',
            'periodic': 'Periodic Trends',
        }

        # find best match
        for term, concept in concept_map.items():
            if term in question_lower:
                if concept in self.nodes:
                    return self.trace_prerequisites(concept)

        # fallback: fuzzy search
        words = question_lower.split()
        for word in words:
            if len(word) > 4:  # skip short words
                matches = self.find_concept(word)
                if matches:
                    return self.trace_prerequisites(matches[0][0])

        return {"error": "Could not map question to concept", "question": question}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Trace prerequisite paths")
    parser.add_argument("--graph", default="/storage/inorganic-chem-class/experiments/results/chemkg_enhanced.json",
                        help="Path to knowledge graph JSON")
    parser.add_argument("--question", "-q", help="Natural language question")
    parser.add_argument("--concept", "-c", help="Direct concept name")
    parser.add_argument("--output", "-o", help="Output JSON file")
    parser.add_argument("--depth", type=int, default=5, help="Max trace depth")
    args = parser.parse_args()

    tracer = PathTracer(args.graph)

    if args.question:
        result = tracer.question_to_path(args.question)
    elif args.concept:
        result = tracer.trace_prerequisites(args.concept, args.depth)
    else:
        # interactive mode
        print("\nPath Tracer - Enter a question or concept (Ctrl+C to exit)")
        while True:
            try:
                query = input("\n> ").strip()
                if not query:
                    continue
                result = tracer.question_to_path(query)
                print(json.dumps(result, indent=2)[:2000] + "...")
            except KeyboardInterrupt:
                break
        return

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Output saved to {args.output}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
