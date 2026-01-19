#!/usr/bin/env python3
"""
Normalization layer for knowledge graph extraction.
Maps variations to canonical names, filters garbage, handles synonyms.
"""

import re
from typing import Dict, List, Optional, Tuple

# =============================================================================
# CANONICAL TOPIC MAPPINGS
# =============================================================================
# Map variations to standard topic names

TOPIC_MAPPINGS = {
    # Coordination chemistry cluster
    "coordination compounds": "Coordination Chemistry",
    "coordination chemistry": "Coordination Chemistry",
    "coordination compound": "Coordination Chemistry",
    "metal complexes": "Coordination Chemistry",

    # Solid state cluster
    "solid state chemistry": "Solid State Chemistry",
    "solid-state chemistry": "Solid State Chemistry",
    "inorganic solid state chemistry": "Solid State Chemistry",
    "inorganic solid-state chemistry": "Solid State Chemistry",
    "crystal structures and lattices": "Solid State Chemistry",
    "crystal structures and packing": "Solid State Chemistry",
    "ionic compounds and lattice energy": "Solid State Chemistry",

    # Electrochemistry cluster
    "electrochemistry": "Electrochemistry",
    "electrochemical reactions": "Electrochemistry",
    "electrochemical processes": "Electrochemistry",
    "redox reactions and electrochemistry": "Electrochemistry",
    "oxidation-reduction chemistry": "Electrochemistry",

    # Main group cluster
    "main group chemistry": "Main Group Chemistry",
    "main group elements": "Main Group Chemistry",
    "chemistry of main group elements": "Main Group Chemistry",

    # Bonding cluster
    "chemical bonding": "Chemical Bonding",
    "molecular structure and bonding": "Chemical Bonding",
    "metallic bonding": "Chemical Bonding",

    # MO Theory cluster
    "molecular orbital theory": "Molecular Orbital Theory",
    "mo theory": "Molecular Orbital Theory",

    # CFT cluster
    "crystal field theory": "Crystal Field Theory",
    "ligand field theory": "Crystal Field Theory",  # closely related
    "cft": "Crystal Field Theory",
    "lft": "Crystal Field Theory",

    # Symmetry cluster
    "symmetry and molecular structure": "Symmetry and Group Theory",
    "group theory and molecular symmetry": "Symmetry and Group Theory",
    "group theory in spectroscopy": "Symmetry and Group Theory",

    # Periodic trends
    "periodic trends": "Periodic Trends",
    "periodic table and elemental properties": "Periodic Trends",
    "periodic trends and atomic properties": "Periodic Trends",
    "electronic structure and periodicity": "Periodic Trends",

    # Acid-base
    "acid-base chemistry": "Acid-Base Chemistry",
    "acids and bases": "Acid-Base Chemistry",

    # Quantum mechanics
    "quantum mechanics": "Quantum Mechanics",
    "quantum mechanics in chemistry": "Quantum Mechanics",

    # Bioinorganic
    "biological inorganic chemistry": "Bioinorganic Chemistry",
    "bioinorganic chemistry and applications": "Bioinorganic Chemistry",

    # Catalysis
    "catalysis with organometallics": "Catalysis",
    "catalytic chemistry and industrial processes": "Catalysis",

    # Spectroscopy
    "spectroscopy": "Spectroscopy",
    "uv-visible spectroscopy": "Spectroscopy",

    # Nuclear
    "radioactivity and nuclear chemistry": "Nuclear Chemistry",

    # Environmental
    "environmental chemistry": "Environmental Chemistry",

    # Cluster chemistry
    "cluster chemistry": "Cluster Chemistry",

    # Transition metals
    "transition metals and their properties": "Transition Metal Chemistry",
    "inorganic chemistry of transition metals": "Transition Metal Chemistry",
}

# Topics to filter out (garbage)
GARBAGE_TOPICS = {
    "inorganic chemistry",  # too generic
    "textbook introduction and publication information",
    "textbook introduction and publisher information",
    "applications in everyday life",
    "history of inorganic chemistry",
    "inorganic chemistry fundamentals",  # too generic
    "inorganic pigments and color chemistry",  # too specific
}

# =============================================================================
# CONCEPT NORMALIZATION
# =============================================================================

CONCEPT_MAPPINGS = {
    # CFT terms
    "cft": "Crystal Field Theory",
    "cfse": "Crystal Field Stabilization Energy",
    "lfse": "Ligand Field Stabilization Energy",
    "lft": "Ligand Field Theory",
    "d-orbital splitting": "d-orbital splitting",
    "d orbital splitting": "d-orbital splitting",
    "delta o": "Δₒ (octahedral splitting)",
    "delta t": "Δₜ (tetrahedral splitting)",
    "δo": "Δₒ (octahedral splitting)",
    "δt": "Δₜ (tetrahedral splitting)",

    # Oxidation state variations
    "oxidation state": "oxidation state",
    "oxidation states": "oxidation state",
    "oxidation number": "oxidation state",

    # Electron config variations
    "electron configuration": "electron configuration",
    "electronic configuration": "electron configuration",
    "electron configurations": "electron configuration",

    # Coordination number
    "coordination number": "coordination number",
    "cn": "coordination number",

    # Electronegativity
    "electronegativity": "electronegativity",
    "en": "electronegativity",

    # Ionization energy
    "ionization energy": "ionization energy",
    "ionisation energy": "ionization energy",
    "ie": "ionization energy",

    # Electron affinity
    "electron affinity": "electron affinity",
    "ea": "electron affinity",

    # MO terms
    "molecular orbital theory": "Molecular Orbital Theory",
    "mo theory": "Molecular Orbital Theory",
    "homo": "HOMO",
    "lumo": "LUMO",

    # Geometry terms
    "octahedral": "octahedral geometry",
    "tetrahedral": "tetrahedral geometry",
    "square planar": "square planar geometry",

    # Bonding terms
    "ionic bonding": "ionic bonding",
    "covalent bonding": "covalent bonding",
    "metallic bonding": "metallic bonding",
    "hybridization": "hybridization",
    "hybridisation": "hybridization",
}

# Concepts to filter (too generic or garbage)
GARBAGE_CONCEPTS = {
    "energy",
    "structure",
    "properties",
    "elements",
    "compounds",
    "reactions",
    "atoms",
    "molecules",
    "chemistry",
    "symbol",
    "molar mass",
    "atomic number",
    "3",  # extracted numbers
    "4",
    "c2",
    "c3",
}

# =============================================================================
# PREREQUISITE NORMALIZATION
# =============================================================================

PREREQ_MAPPINGS = {
    "periodic trends": "Periodic Trends",
    "understanding of periodic trends": "Periodic Trends",
    "basic periodic trends": "Periodic Trends",

    "electron configuration": "Electron Configuration",
    "electronic configuration": "Electron Configuration",
    "basic knowledge of atomic structure": "Atomic Structure",

    "coordination chemistry basics": "Coordination Chemistry Fundamentals",
    "coordination chemistry": "Coordination Chemistry Fundamentals",
    "coordination chemistry fundamentals": "Coordination Chemistry Fundamentals",
    "basic coordination chemistry": "Coordination Chemistry Fundamentals",

    "redox reactions": "Redox Chemistry",
    "oxidation-reduction reactions": "Redox Chemistry",

    "oxidation states": "Oxidation States",
    "understanding of oxidation states": "Oxidation States",

    "understanding of ionic bonding": "Ionic Bonding",
    "ionic bonding": "Ionic Bonding",

    "crystal field theory basics": "Crystal Field Theory",
    "crystal field theory": "Crystal Field Theory",
    "basic cft": "Crystal Field Theory",

    "hybridization concepts": "Hybridization",
    "hybridization": "Hybridization",

    "acid-base reactions": "Acid-Base Chemistry",
    "acid-base chemistry": "Acid-Base Chemistry",

    "electronic configurations of transition metals": "Transition Metal Electron Configuration",
    "transition metal chemistry": "Transition Metal Chemistry",

    "reaction mechanisms": "Reaction Mechanisms",
    "ligand field theory": "Ligand Field Theory",
}

# =============================================================================
# NORMALIZATION FUNCTIONS
# =============================================================================

def normalize_text(text: str) -> str:
    """basic text normalization - lowercase, strip, single spaces"""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip().lower())


def normalize_topic(topic: str) -> Optional[str]:
    """normalize topic to canonical name, return None if garbage"""
    if not topic:
        return None

    normalized = normalize_text(topic)

    # check garbage first
    if normalized in GARBAGE_TOPICS:
        return None

    # check mappings
    if normalized in TOPIC_MAPPINGS:
        return TOPIC_MAPPINGS[normalized]

    # if not in mappings, title case and return
    # (unknown topic - might need to add to mappings)
    return topic.strip().title()


def normalize_concept(concept: str) -> Optional[str]:
    """normalize concept, return None if garbage"""
    if not concept:
        return None

    normalized = normalize_text(concept)

    # check garbage
    if normalized in GARBAGE_CONCEPTS:
        return None

    # filter very short concepts
    if len(normalized) < 3:
        return None

    # filter pure numbers
    if normalized.isdigit():
        return None

    # check mappings
    if normalized in CONCEPT_MAPPINGS:
        return CONCEPT_MAPPINGS[normalized]

    # return original (preserving case for proper nouns)
    return concept.strip()


def normalize_prerequisite(prereq: str) -> Optional[str]:
    """normalize prerequisite to canonical name"""
    if not prereq:
        return None

    normalized = normalize_text(prereq)

    # check mappings
    if normalized in PREREQ_MAPPINGS:
        return PREREQ_MAPPINGS[normalized]

    # title case unknown prereqs
    return prereq.strip().title()


def normalize_extraction(extraction: Dict) -> Dict:
    """normalize an entire extraction result"""
    result = {}

    # normalize topic
    topic = extraction.get("topic", "")
    normalized_topic = normalize_topic(topic)
    result["topic"] = normalized_topic
    result["topic_raw"] = topic  # keep original for debugging

    # normalize subtopic (less aggressive - keep as-is mostly)
    subtopic = extraction.get("subtopic", "")
    result["subtopic"] = subtopic.strip() if subtopic else None

    # normalize concepts
    concepts = extraction.get("key_concepts", [])
    normalized_concepts = []
    for c in concepts:
        nc = normalize_concept(c)
        if nc and nc not in normalized_concepts:
            normalized_concepts.append(nc)
    result["key_concepts"] = normalized_concepts

    # normalize prerequisites
    prereqs = extraction.get("prerequisites", [])
    normalized_prereqs = []
    for p in prereqs:
        np = normalize_prerequisite(p)
        if np and np not in normalized_prereqs:
            normalized_prereqs.append(np)
    result["prerequisites"] = normalized_prereqs

    # normalize leads_to
    leads_to = extraction.get("leads_to", [])
    normalized_leads = []
    for l in leads_to:
        # use topic normalization for leads_to
        nl = normalize_topic(l)
        if nl and nl not in normalized_leads:
            normalized_leads.append(nl)
    result["leads_to"] = normalized_leads

    # keep confidence
    result["confidence"] = extraction.get("confidence", 0.0)

    return result


# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def analyze_normalization(extractions: List[Dict]) -> Dict:
    """analyze normalization results"""
    from collections import Counter

    topics = Counter()
    subtopics = Counter()
    concepts = Counter()
    prereqs = Counter()
    leads_to = Counter()

    filtered_topics = 0
    filtered_concepts = 0

    for ext in extractions:
        norm = normalize_extraction(ext.get("extraction", ext))

        if norm["topic"]:
            topics[norm["topic"]] += 1
        else:
            filtered_topics += 1

        if norm["subtopic"]:
            subtopics[norm["subtopic"]] += 1

        for c in norm["key_concepts"]:
            concepts[c] += 1

        # count filtered concepts
        raw_concepts = ext.get("extraction", ext).get("key_concepts", [])
        filtered_concepts += len(raw_concepts) - len(norm["key_concepts"])

        for p in norm["prerequisites"]:
            prereqs[p] += 1

        for l in norm["leads_to"]:
            leads_to[l] += 1

    return {
        "topics": dict(topics),
        "subtopics": dict(subtopics),
        "concepts": dict(concepts),
        "prerequisites": dict(prereqs),
        "leads_to": dict(leads_to),
        "stats": {
            "unique_topics": len(topics),
            "unique_subtopics": len(subtopics),
            "unique_concepts": len(concepts),
            "unique_prereqs": len(prereqs),
            "unique_leads_to": len(leads_to),
            "filtered_topics": filtered_topics,
            "filtered_concepts": filtered_concepts,
        }
    }


def print_analysis(analysis: Dict):
    """print normalized analysis"""
    print("\n" + "=" * 60)
    print("NORMALIZED ANALYSIS")
    print("=" * 60)

    stats = analysis["stats"]
    print(f"\n📊 TOPICS ({stats['unique_topics']} unique, {stats['filtered_topics']} filtered)")
    print("-" * 40)
    for topic, count in sorted(analysis["topics"].items(), key=lambda x: -x[1])[:20]:
        print(f"  {count:3d}x | {topic}")

    print(f"\n📊 KEY CONCEPTS ({stats['unique_concepts']} unique, {stats['filtered_concepts']} filtered)")
    print("-" * 40)
    for concept, count in sorted(analysis["concepts"].items(), key=lambda x: -x[1])[:25]:
        print(f"  {count:3d}x | {concept}")

    print(f"\n🔗 PREREQUISITES ({stats['unique_prereqs']} unique)")
    print("-" * 40)
    for prereq, count in sorted(analysis["prerequisites"].items(), key=lambda x: -x[1])[:15]:
        print(f"  {count:3d}x | {prereq}")

    print(f"\n➡️  LEADS TO ({stats['unique_leads_to']} unique)")
    print("-" * 40)
    for lt, count in sorted(analysis["leads_to"].items(), key=lambda x: -x[1])[:15]:
        print(f"  {count:3d}x | {lt}")

    print("\n" + "=" * 60)
    print("SUMMARY (after normalization)")
    print("=" * 60)
    print(f"  Topics:     {stats['unique_topics']:4d} unique (target: 15-25)")
    print(f"  Subtopics:  {stats['unique_subtopics']:4d} unique")
    print(f"  Concepts:   {stats['unique_concepts']:4d} unique")
    print(f"  Filtered:   {stats['filtered_topics']} topics, {stats['filtered_concepts']} concepts")


# =============================================================================
# MAIN - Test normalization on existing data
# =============================================================================

if __name__ == "__main__":
    import json
    from pathlib import Path

    # load experiment data
    data_file = Path("experiments/results/granularity_experiment_500.json")
    if not data_file.exists():
        data_file = Path("experiments/results/granularity_experiment.json")

    print(f"Loading data from {data_file}...")
    with open(data_file) as f:
        data = json.load(f)

    print(f"Loaded {len(data)} extractions")

    # analyze with normalization
    analysis = analyze_normalization(data)
    print_analysis(analysis)

    # save normalized analysis
    output_file = Path("experiments/results/normalized_analysis.json")
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    print(f"\nSaved to {output_file}")
