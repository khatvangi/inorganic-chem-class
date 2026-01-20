#!/usr/bin/env python3
"""
Meta-Book Generator for CHEM 361 Inorganic Chemistry

Combines:
1. Knowledge graph (chemkg_enhanced.json) - prerequisites, pagerank, mentions
2. Textbook analysis (textbook_analysis_v3.json) - best sources per topic
3. Hierarchical model - 4 scales (QUANTUM → ELECTRONIC → STRUCTURAL → DESCRIPTIVE)
4. Hub-based curriculum - Foundations → Hubs → Capstones

Outputs:
- metabook.json - Full compiled meta-book
- Individual lesson files
- Topic metadata
- Assessment items
- Learning paths
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

# ============================================================================
# CONFIGURATION
# ============================================================================

# Scale classification keywords
SCALE_KEYWORDS = {
    "QUANTUM": [
        "quantum", "orbital", "wave function", "electron configuration",
        "spin", "quantum number", "aufbau", "hund", "pauli", "radial",
        "angular", "node", "probability density", "schrodinger", "hamiltonian",
        "atomic orbital", "hybridization", "s orbital", "p orbital", "d orbital",
        "f orbital", "relativistic", "spin-orbit"
    ],
    "ELECTRONIC": [
        "crystal field", "ligand field", "molecular orbital", "bonding",
        "antibonding", "homo", "lumo", "band gap", "band theory", "d-d transition",
        "charge transfer", "spectrochemical", "cfse", "splitting", "magnetism",
        "paramagnetic", "diamagnetic", "ferromagnetic", "electronic spectrum",
        "uv-vis", "absorption", "term symbol", "racah", "tanabe-sugano",
        "jahn-teller", "nephelauxetic"
    ],
    "STRUCTURAL": [
        "geometry", "coordination", "octahedral", "tetrahedral", "square planar",
        "trigonal", "linear", "symmetry", "point group", "isomer", "stereoisomer",
        "enantiomer", "diastereomer", "fac", "mer", "cis", "trans", "crystal structure",
        "unit cell", "lattice", "packing", "coordination number", "nomenclature",
        "naming", "formula", "complex ion", "chelate", "bidentate", "polydentate",
        "linkage isomer", "ionization isomer"
    ],
    "DESCRIPTIVE": [
        "periodic trend", "electronegativity", "ionization energy", "electron affinity",
        "atomic radius", "ionic radius", "group", "period", "s-block", "p-block",
        "d-block", "f-block", "alkali", "alkaline earth", "halogen", "noble gas",
        "transition metal", "lanthanide", "actinide", "main group", "reactivity",
        "oxidation state", "common ion", "color", "flame test", "solubility",
        "industrial", "biological", "environmental"
    ]
}

# Hub topics (knowledge bottlenecks)
HUB_TOPICS = [
    "Acid-Base Chemistry",
    "Crystal Field Theory", 
    "Molecular Orbital Theory",
    "Redox Chemistry",
    "Periodic Trends",
    "Coordination Chemistry",
    "Ionic Bonding",
    "Atomic Structure",
    "Thermodynamics",
    "Kinetics",
    "Symmetry And Group Theory",
    "Solid State Chemistry",
    "Organometallic Chemistry"
]

# Best source mapping (from TEXTBOOK_ANALYSIS_V3_SUMMARY.md)
BEST_SOURCES = {
    "coordination": {"primary": "ic_tina", "secondary": "Atkins_Shriver"},
    "crystal_field": {"primary": "concise_ic_jd_lee", "secondary": "ic_tina"},
    "main_group_p": {"primary": "descriptive_ic", "secondary": "descriptive_ic_house"},
    "main_group_s": {"primary": "concise_ic_jd_lee", "secondary": "descriptive_ic"},
    "transition_metals": {"primary": "descriptive_ic_house", "secondary": "descriptive_ic"},
    "mechanisms": {"primary": "descriptive_ic", "secondary": "descriptive_ic_house"},
    "examples": {"primary": "ic_tina", "secondary": "Atkins_Shriver"},
    "theory": {"primary": "descriptive_ic", "secondary": "concise_ic_jd_lee"},
    "default": {"primary": "ic_tina", "secondary": "Atkins_Shriver"}
}

# Bloom's taxonomy levels
BLOOM_LEVELS = ["remember", "understand", "apply", "analyze", "evaluate", "create"]

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class TopicMetadata:
    """Metadata for a single topic"""
    id: str
    name: str
    scale: str
    tree: str
    pagerank: float
    mentions: int
    in_degree: int
    out_degree: int
    hub_score: float
    prerequisites: List[str]
    leads_to: List[str]
    subtopics: List[str]
    best_sources: Dict[str, Dict]
    scale_context: Dict[str, str]

@dataclass
class LearningObjective:
    """A single learning objective"""
    id: str
    text: str
    bloom_level: str
    scale: str
    assessment_type: str

@dataclass 
class Lesson:
    """A single lesson in the meta-book"""
    id: str
    title: str
    unit: str
    session: int
    duration_minutes: int
    scale: Dict
    topic: Dict
    prerequisites: Dict
    learning_objectives: List[Dict]
    content_synthesis: Dict
    subtopics: List[Dict]
    worked_examples: List[Dict]
    assessment_items: Dict
    connections: Dict

@dataclass
class Unit:
    """A course unit containing multiple lessons"""
    id: str
    name: str
    scale: str
    sessions: int
    weeks: str
    slos: List[str]
    lessons: List[str]
    hub_topics: List[str]
    assessment: Dict

# ============================================================================
# SCALE CLASSIFICATION
# ============================================================================

def classify_scale(topic_name: str, subtopics: List[str] = None) -> str:
    """
    Classify a topic into one of 4 scales based on keywords.
    
    Priority: QUANTUM > ELECTRONIC > STRUCTURAL > DESCRIPTIVE
    (Deeper scales override shallower ones)
    """
    text = topic_name.lower()
    if subtopics:
        text += " " + " ".join(s.lower() for s in subtopics)
    
    scores = {scale: 0 for scale in SCALE_KEYWORDS}
    
    for scale, keywords in SCALE_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[scale] += 1
    
    # Priority ordering: deeper scales win ties
    priority = ["QUANTUM", "ELECTRONIC", "STRUCTURAL", "DESCRIPTIVE"]
    
    max_score = max(scores.values())
    if max_score == 0:
        return "DESCRIPTIVE"  # Default
    
    for scale in priority:
        if scores[scale] == max_score:
            return scale
    
    return "DESCRIPTIVE"

def infer_tree(topic_name: str, scale: str) -> str:
    """Infer which tree within a scale a topic belongs to"""
    name_lower = topic_name.lower()
    
    trees = {
        "QUANTUM": {
            "atomic_structure": ["atomic", "orbital", "electron config", "quantum number"],
            "quantum_mechanics": ["wave function", "schrodinger", "hamiltonian", "spin"],
            "relativistic": ["relativistic", "spin-orbit"]
        },
        "ELECTRONIC": {
            "crystal_field_theory": ["crystal field", "cfse", "splitting", "spectrochemical"],
            "molecular_orbital_theory": ["molecular orbital", "mo theory", "homo", "lumo", "band"],
            "bonding_theories": ["bonding", "valence bond", "hybridization"],
            "spectroscopy": ["spectrum", "absorption", "uv-vis", "transition"]
        },
        "STRUCTURAL": {
            "coordination_geometry": ["coordination", "geometry", "octahedral", "tetrahedral"],
            "crystal_structures": ["crystal structure", "unit cell", "lattice", "packing"],
            "symmetry": ["symmetry", "point group", "character"],
            "isomerism": ["isomer", "stereoisomer", "enantiomer"]
        },
        "DESCRIPTIVE": {
            "periodic_trends": ["periodic", "trend", "electronegativity", "radius"],
            "main_group": ["main group", "s-block", "p-block", "alkali", "halogen"],
            "transition_metals": ["transition metal", "d-block"],
            "lanthanides_actinides": ["lanthanide", "actinide", "f-block"],
            "applications": ["industrial", "biological", "environmental", "catalysis"]
        }
    }
    
    if scale in trees:
        for tree_name, keywords in trees[scale].items():
            for kw in keywords:
                if kw in name_lower:
                    return tree_name
    
    return f"{scale.lower()}_general"

def get_best_source(topic_name: str, scale: str) -> Dict[str, Dict]:
    """Determine best textbook sources for a topic"""
    name_lower = topic_name.lower()
    
    # Topic-specific matching
    if "coordination" in name_lower and "crystal" not in name_lower:
        return BEST_SOURCES["coordination"]
    elif "crystal field" in name_lower or "cfse" in name_lower:
        return BEST_SOURCES["crystal_field"]
    elif any(x in name_lower for x in ["p-block", "halogen", "noble gas", "carbon group"]):
        return BEST_SOURCES["main_group_p"]
    elif any(x in name_lower for x in ["s-block", "alkali", "alkaline earth"]):
        return BEST_SOURCES["main_group_s"]
    elif "transition" in name_lower:
        return BEST_SOURCES["transition_metals"]
    elif "mechanism" in name_lower or "reaction" in name_lower:
        return BEST_SOURCES["mechanisms"]
    
    # Scale-based fallback
    if scale == "ELECTRONIC":
        return BEST_SOURCES["theory"]
    elif scale == "DESCRIPTIVE":
        return BEST_SOURCES["main_group_p"]
    
    return BEST_SOURCES["default"]

# ============================================================================
# KNOWLEDGE GRAPH PROCESSING
# ============================================================================

def load_knowledge_graph(path: str) -> Dict:
    """Load the enhanced knowledge graph"""
    with open(path, 'r') as f:
        return json.load(f)

def extract_topics(kg: Dict) -> Dict[str, TopicMetadata]:
    """Extract topic metadata from knowledge graph"""
    topics = {}
    
    nodes = kg.get("nodes", kg.get("topics", []))
    edges = kg.get("edges", kg.get("relationships", []))
    
    # Build adjacency lists
    prereqs_for = defaultdict(list)  # topic -> what it's a prereq for
    prereqs_of = defaultdict(list)   # topic -> its prerequisites
    
    for edge in edges:
        source = edge.get("source", edge.get("from", ""))
        target = edge.get("target", edge.get("to", ""))
        rel_type = edge.get("type", edge.get("relation", ""))
        
        if rel_type in ["prerequisite_for", "prerequisite"]:
            prereqs_for[source].append(target)
            prereqs_of[target].append(source)
        elif rel_type == "leads_to":
            prereqs_for[source].append(target)
    
    # Process each node
    for node in nodes:
        if isinstance(node, dict):
            name = node.get("name", node.get("id", node.get("topic", "")))
            pagerank = node.get("pagerank", 0.0)
            mentions = node.get("mentions", node.get("count", 0))
            subtopics = node.get("subtopics", [])
        else:
            name = str(node)
            pagerank = 0.0
            mentions = 0
            subtopics = []
        
        if not name or mentions < 5:  # Filter low-mention noise
            continue
        
        # Classify
        scale = classify_scale(name, subtopics)
        tree = infer_tree(name, scale)
        
        # Calculate hub score (normalized degree centrality)
        in_deg = len(prereqs_of.get(name, []))
        out_deg = len(prereqs_for.get(name, []))
        total_deg = in_deg + out_deg
        hub_score = min(1.0, total_deg / 50)  # Normalize to [0,1]
        
        # Best sources
        sources = get_best_source(name, scale)
        
        # Create metadata
        topic_id = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
        
        topics[name] = TopicMetadata(
            id=f"topic_{topic_id}",
            name=name,
            scale=scale,
            tree=tree,
            pagerank=pagerank,
            mentions=mentions,
            in_degree=in_deg,
            out_degree=out_deg,
            hub_score=hub_score,
            prerequisites=prereqs_of.get(name, []),
            leads_to=prereqs_for.get(name, []),
            subtopics=subtopics if isinstance(subtopics, list) else [],
            best_sources={
                "explanation": {"source": sources["primary"], "strength": "primary"},
                "examples": {"source": sources.get("secondary", sources["primary"]), "strength": "secondary"}
            },
            scale_context={
                "why_this_scale": f"Topic operates primarily at {scale} level",
                "escalation_trigger": f"Why questions about {name}",
                "escalation_target": get_escalation_target(scale)
            }
        )
    
    return topics

def get_escalation_target(scale: str) -> str:
    """Get the deeper scale to escalate to for 'why' questions"""
    escalation = {
        "DESCRIPTIVE": "STRUCTURAL or ELECTRONIC",
        "STRUCTURAL": "ELECTRONIC",
        "ELECTRONIC": "QUANTUM",
        "QUANTUM": "None (fundamental level)"
    }
    return escalation.get(scale, "ELECTRONIC")

# ============================================================================
# CURRICULUM ORDERING (Combined: PageRank Order + Hub Checkpoints)
# ============================================================================

def order_topics_by_curriculum(topics: Dict[str, TopicMetadata]) -> List[str]:
    """
    COMBINED PEDAGOGY:
    - ORDER by PageRank (foundational topics first)
    - CHECKPOINT at Hubs (high-degree bottleneck topics)

    PageRank answers: "What should I learn FIRST?"
    Hub score answers: "Where will I get STUCK?"
    """

    # Primary ordering: PageRank (foundations first)
    # This ensures prerequisites are taught before dependent topics
    by_pagerank = sorted(
        topics.items(),
        key=lambda x: (-x[1].pagerank, -x[1].mentions),  # High PR first, then mentions
    )

    ordered = [name for name, _ in by_pagerank]

    return ordered


def identify_hub_checkpoints(topics: Dict[str, TopicMetadata], ordered: List[str]) -> Dict[str, Dict]:
    """
    Identify hub topics that need checkpoints.
    Students should be assessed after these bottleneck topics.

    Hub = high total degree (in + out) = gateway topic
    """
    checkpoints = {}

    for name in ordered:
        if name not in topics:
            continue
        meta = topics[name]

        # Hub criteria: high connectivity OR explicitly marked
        is_hub = (
            meta.hub_score > 0.4 or
            name in HUB_TOPICS or
            (meta.in_degree >= 3 and meta.out_degree >= 3)
        )

        if is_hub:
            # Find position in ordered list
            try:
                position = ordered.index(name)
            except ValueError:
                position = -1

            checkpoints[name] = {
                "position": position,
                "hub_score": meta.hub_score,
                "total_degree": meta.in_degree + meta.out_degree,
                "checkpoint_type": "mastery_check",
                "threshold": 0.75,  # 75% required to proceed
                "remediation": f"review_{name.lower().replace(' ', '_')}",
                "why_checkpoint": f"Bottleneck topic: {meta.out_degree} topics depend on this"
            }

    return checkpoints

# ============================================================================
# LESSON GENERATION
# ============================================================================

def generate_learning_objectives(topic: TopicMetadata, lesson_num: int) -> List[Dict]:
    """Generate learning objectives for a topic"""
    objectives = []
    
    # Base objective: understand the concept
    objectives.append({
        "id": f"LO_{lesson_num}_1",
        "text": f"Define and explain {topic.name}",
        "bloom_level": "understand",
        "scale": topic.scale,
        "assessment_type": "short_answer"
    })
    
    # Application objective
    if topic.scale in ["ELECTRONIC", "STRUCTURAL"]:
        objectives.append({
            "id": f"LO_{lesson_num}_2",
            "text": f"Apply {topic.name} to predict chemical properties",
            "bloom_level": "apply",
            "scale": topic.scale,
            "assessment_type": "problem_solving"
        })
    
    # Analysis objective for hubs
    if topic.hub_score > 0.5:
        objectives.append({
            "id": f"LO_{lesson_num}_3",
            "text": f"Analyze how {topic.name} connects to related concepts",
            "bloom_level": "analyze",
            "scale": topic.scale,
            "assessment_type": "essay"
        })
    
    return objectives

def generate_lesson(topic: TopicMetadata, lesson_num: int, unit_id: str) -> Lesson:
    """Generate a complete lesson from topic metadata"""
    
    # Determine which scales are touched
    touched_scales = []
    for prereq in topic.prerequisites[:3]:  # Look at top 3 prereqs
        prereq_scale = classify_scale(prereq)
        if prereq_scale != topic.scale and prereq_scale not in touched_scales:
            touched_scales.append(prereq_scale)
    
    # Generate subtopics with time allocation
    subtopics = []
    base_time = 75 // max(1, len(topic.subtopics) + 1)
    for i, st in enumerate(topic.subtopics[:5]):  # Max 5 subtopics
        subtopics.append({
            "name": st,
            "time_allocation": base_time,
            "key_points": [],
            "common_misconceptions": []
        })
    
    # Generate worked examples
    examples = []
    if topic.scale == "ELECTRONIC":
        examples.append({
            "problem": f"Apply {topic.name} to predict properties of a transition metal complex",
            "type": "calculation",
            "difficulty": "medium",
            "solution_steps": ["Identify key parameters", "Apply theory", "Interpret result"],
            "source": f"adapted from {topic.best_sources['explanation']['source']}"
        })
    
    return Lesson(
        id=f"lesson_{lesson_num:02d}",
        title=topic.name,
        unit=unit_id,
        session=lesson_num,
        duration_minutes=75,
        scale={
            "primary": topic.scale,
            "touches": touched_scales,
            "escalation_from": topic.prerequisites[0] if topic.prerequisites else None
        },
        topic={
            "name": topic.name,
            "pagerank": topic.pagerank,
            "mentions": topic.mentions,
            "hub_score": topic.hub_score
        },
        prerequisites={
            "required": topic.prerequisites[:3],
            "recommended": topic.prerequisites[3:5] if len(topic.prerequisites) > 3 else [],
            "scale_prerequisites": {topic.scale: topic.prerequisites[:2]}
        },
        learning_objectives=generate_learning_objectives(topic, lesson_num),
        content_synthesis={
            "best_explanation": topic.best_sources["explanation"],
            "best_examples": topic.best_sources["examples"],
            "cross_references": []
        },
        subtopics=subtopics,
        worked_examples=examples,
        assessment_items={
            "formative": [
                {"type": "clicker", "question": f"Quick check on {topic.name}"}
            ],
            "summative": {
                "quiz_questions": [f"quiz_{lesson_num}_q1"],
                "exam_questions": []
            }
        },
        connections={
            "forward": topic.leads_to[:3],
            "backward": topic.prerequisites[:3],
            "lateral": [],
            "applications": []
        }
    )

# ============================================================================
# UNIT GENERATION (PageRank-ordered with Hub Checkpoints)
# ============================================================================

def generate_units(topics: Dict[str, TopicMetadata], ordered_topics: List[str]) -> List[Unit]:
    """
    Generate course units based on PageRank order.
    Units are divided by natural breaks in the curriculum.

    Unit 1: High PageRank topics (foundations)
    Unit 2: Medium PageRank topics (core concepts)
    Unit 3: Lower PageRank topics (applications/integration)
    """

    units = []
    total_lessons = min(23, len(ordered_topics))

    # Divide into 3 units: 8 + 9 + 6 = 23 lessons
    unit_sizes = [8, 9, 6]

    # Unit 1: Foundations (highest PageRank topics)
    units.append(Unit(
        id="unit_1",
        name="Foundations (PageRank Top Tier)",
        scale="MIXED",
        sessions=unit_sizes[0],
        weeks="1-5",
        slos=["SLO1", "SLO2"],
        lessons=[f"lesson_{i+1:02d}" for i in range(unit_sizes[0])],
        hub_topics=[t for t in ordered_topics[:unit_sizes[0]]
                   if t in topics and topics[t].hub_score > 0.3],
        assessment={"diagnostic": True, "midterm1": True, "quizzes": [1, 2, 3]}
    ))

    # Unit 2: Core Concepts (medium PageRank)
    start_idx = unit_sizes[0]
    units.append(Unit(
        id="unit_2",
        name="Core Concepts (PageRank Mid Tier)",
        scale="ELECTRONIC",
        sessions=unit_sizes[1],
        weeks="6-10",
        slos=["SLO2", "SLO3", "SLO4"],
        lessons=[f"lesson_{start_idx+i+1:02d}" for i in range(unit_sizes[1])],
        hub_topics=[t for t in ordered_topics[start_idx:start_idx+unit_sizes[1]]
                   if t in topics and topics[t].hub_score > 0.3],
        assessment={"midterm2": True, "quizzes": [4, 5, 6]}
    ))

    # Unit 3: Applications & Integration
    start_idx = unit_sizes[0] + unit_sizes[1]
    units.append(Unit(
        id="unit_3",
        name="Applications & Integration",
        scale="DESCRIPTIVE",
        sessions=unit_sizes[2],
        weeks="11-15",
        slos=["SLO4", "SLO5", "SLO6"],
        lessons=[f"lesson_{start_idx+i+1:02d}" for i in range(unit_sizes[2])],
        hub_topics=[],
        assessment={"final": True, "quizzes": [7, 8]}
    ))

    return units

# ============================================================================
# LEARNING PATHS (with Hub Checkpoints)
# ============================================================================

def generate_learning_paths(topics: Dict[str, TopicMetadata], lessons: List[Lesson],
                           hub_checkpoints: Dict[str, Dict]) -> Dict:
    """
    Generate learning paths with:
    - Standard path (PageRank ordered)
    - Hub checkpoints (mastery gates at bottleneck topics)
    - Remediation paths (for students who fail hub checks)
    - Acceleration paths (for advanced students)
    """

    # Build lesson name to ID mapping
    lesson_map = {l.title: l.id for l in lessons}

    # Convert hub checkpoints to lesson-based checkpoints
    checkpoint_list = []
    for topic_name, checkpoint in hub_checkpoints.items():
        if topic_name in lesson_map:
            lesson_id = lesson_map[topic_name]
            checkpoint_list.append({
                "topic": topic_name,
                "after_lesson": lesson_id,
                "hub_score": checkpoint["hub_score"],
                "total_degree": checkpoint["total_degree"],
                "assessment": f"hub_check_{topic_name.lower().replace(' ', '_')}",
                "threshold": checkpoint["threshold"],
                "remediation": checkpoint["remediation"],
                "why": checkpoint["why_checkpoint"]
            })

    # Sort checkpoints by lesson position
    checkpoint_list.sort(key=lambda x: x["after_lesson"])

    return {
        "pedagogy_model": {
            "ordering": "PageRank (foundational topics first)",
            "checkpoints": "Hub-based (bottleneck topics flagged)",
            "rationale": "PageRank ensures prerequisites met; Hubs catch struggling students early"
        },
        "standard_path": {
            "name": "PageRank-Ordered Curriculum",
            "description": "Topics ordered by foundational importance (PageRank), with mastery checks at hub topics",
            "lessons": [l.id for l in lessons]
        },
        "hub_checkpoints": checkpoint_list[:10],  # Top 10 hub checkpoints
        "remediation_paths": {
            "weak_atomic_structure": {
                "trigger": "hub_check fails on Atomic Structure",
                "supplemental": ["review_orbitals", "practice_electron_config"],
                "resources": ["JD Lee Ch.1", "ic_tina orbital module"]
            },
            "weak_periodic_trends": {
                "trigger": "hub_check fails on Periodic Trends",
                "supplemental": ["review_periodic_table", "practice_trends"],
                "resources": ["Rodgers Ch.2", "periodic trends worksheet"]
            },
            "weak_bonding": {
                "trigger": "hub_check fails on Chemical Bonding or MO Theory",
                "supplemental": ["review_lewis", "practice_mo_diagrams"],
                "resources": ["Atkins Ch.3", "MO diagram practice"]
            },
            "weak_coordination": {
                "trigger": "hub_check fails on Coordination Chemistry",
                "supplemental": ["review_nomenclature", "practice_isomers"],
                "resources": ["ic_tina coordination module"]
            },
            "weak_cft": {
                "trigger": "hub_check fails on Crystal Field Theory",
                "supplemental": ["review_d_orbitals", "practice_cfse"],
                "resources": ["JD Lee CFT chapter", "Tanabe-Sugano practice"]
            }
        },
        "acceleration_paths": {
            "strong_foundation": {
                "trigger": "pretest_score > 90% AND first hub_check > 90%",
                "action": "Skip review lessons, proceed to applications",
                "skip_lessons": ["lesson_01", "lesson_02"]
            }
        },
        "checkpoint_summary": {
            "total_hubs_identified": len(hub_checkpoints),
            "checkpoints_in_curriculum": len(checkpoint_list),
            "average_threshold": 0.75,
            "remediation_available": True
        }
    }

# ============================================================================
# ASSESSMENT GENERATION
# ============================================================================

def generate_assessments(topics: Dict[str, TopicMetadata], lessons: List[Lesson]) -> Dict:
    """Generate assessment items aligned with lessons and learning objectives"""
    
    assessments = {
        "quizzes": {},
        "exams": {},
        "formative": {}
    }
    
    for lesson in lessons:
        topic_name = lesson.topic["name"]
        if topic_name not in topics:
            continue
        
        topic = topics[topic_name]
        
        # Generate quiz questions
        quiz_id = f"quiz_{lesson.session}"
        assessments["quizzes"][quiz_id] = {
            "lesson": lesson.id,
            "topic": topic_name,
            "questions": [
                {
                    "id": f"{quiz_id}_q1",
                    "type": "short_answer",
                    "stem": f"Explain the key principles of {topic_name}.",
                    "points": 5,
                    "bloom_level": "understand",
                    "scale": topic.scale
                },
                {
                    "id": f"{quiz_id}_q2",
                    "type": "problem",
                    "stem": f"Apply {topic_name} to the following scenario...",
                    "points": 10,
                    "bloom_level": "apply",
                    "scale": topic.scale
                }
            ]
        }
        
        # Formative assessments
        assessments["formative"][lesson.id] = [
            {
                "type": "clicker",
                "question": f"Which of the following best describes {topic_name}?",
                "timing": "start"
            },
            {
                "type": "think_pair_share",
                "prompt": f"How does {topic_name} relate to {topic.prerequisites[0] if topic.prerequisites else 'previous concepts'}?",
                "timing": "middle"
            }
        ]
    
    # Generate exam questions (sample)
    assessments["exams"]["midterm"] = {
        "covers_lessons": ["lesson_01", "lesson_08"],
        "questions": [
            {
                "id": "midterm_q1",
                "type": "essay",
                "stem": "Explain how Crystal Field Theory builds on atomic orbital concepts.",
                "points": 20,
                "bloom_level": "analyze",
                "rubric": {
                    "full_credit": "Connects CFT to d-orbital shapes, explains splitting mechanism",
                    "partial_credit": "Mentions orbitals but incomplete connection"
                }
            }
        ]
    }
    
    return assessments

# ============================================================================
# META-BOOK ASSEMBLY
# ============================================================================

def generate_metabook(kg_path: str, output_dir: str):
    """Generate the complete meta-book from knowledge graph"""
    
    print("Loading knowledge graph...")
    kg = load_knowledge_graph(kg_path)
    
    print("Extracting topics...")
    topics = extract_topics(kg)
    print(f"  Extracted {len(topics)} topics")
    
    print("Ordering topics by curriculum structure...")
    ordered = order_topics_by_curriculum(topics)
    
    print("Generating units...")
    units = generate_units(topics, ordered)
    
    print("Generating lessons...")
    lessons = []
    lesson_num = 1
    used_topics = set()
    
    # Generate lessons by unit phase
    for unit in units:
        unit_lesson_count = 0
        max_lessons = unit.sessions if unit.sessions > 0 else 8
        
        for topic_name in ordered:
            if topic_name in used_topics:
                continue
            if topic_name not in topics:
                continue
            if lesson_num > 23:  # Cap at 23 lessons
                break
            if unit_lesson_count >= max_lessons:
                break
            
            topic = topics[topic_name]
            
            # Phase-based filtering (relaxed)
            include = False
            if unit.id == "unit_1":  # Foundations: foundational topics
                include = topic.out_degree >= 2 or topic.pagerank > 0.003
            elif unit.id == "unit_2":  # Hubs: hub topics or moderate connectivity
                include = topic.hub_score > 0.2 or (topic.in_degree >= 1 and topic.out_degree >= 1)
            elif unit.id == "unit_3":  # Capstones: integration topics
                include = topic.in_degree >= 2 or topic.mentions > 150
            
            if not include:
                continue
            
            lesson = generate_lesson(topic, lesson_num, unit.id)
            lessons.append(lesson)
            used_topics.add(topic_name)
            lesson_num += 1
            unit_lesson_count += 1
    
    print(f"  Generated {len(lessons)} lessons")

    print("Identifying hub checkpoints...")
    hub_checkpoints = identify_hub_checkpoints(topics, ordered)
    print(f"  Identified {len(hub_checkpoints)} hub checkpoints")

    print("Generating learning paths...")
    paths = generate_learning_paths(topics, lessons, hub_checkpoints)
    
    print("Generating assessments...")
    assessments = generate_assessments(topics, lessons)
    
    # Assemble meta-book
    metabook = {
        "meta": {
            "version": "2.0.0",
            "course": "CHEM 361",
            "title": "Inorganic Chemistry Meta-Book",
            "generated": datetime.now().isoformat(),
            "sources": {
                "knowledge_graph": kg_path,
                "textbooks": list(set(
                    t.best_sources["explanation"]["source"]
                    for t in topics.values()
                )),
                "model": "hierarchical_4_scale"
            },
            "pedagogy_model": {
                "description": "Combined PageRank Order + Hub Checkpoints",
                "ordering_method": "PageRank (foundational topics first)",
                "checkpoint_method": "Hub-based (bottleneck detection)",
                "rationale": {
                    "pagerank": "Ensures prerequisites are taught before dependent topics",
                    "hubs": "Identifies where students get stuck, enables early intervention"
                },
                "combined_benefit": "Students learn in correct order AND get checked at bottlenecks"
            }
        },
        "units": [asdict(u) for u in units],
        "lessons": [asdict(l) for l in lessons],
        "topics": {name: asdict(t) for name, t in topics.items()},
        "hub_checkpoints": hub_checkpoints,
        "assessments": assessments,
        "learning_paths": paths
    }
    
    # Create output directory
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    # Write main meta-book
    print(f"Writing meta-book to {output_dir}...")
    with open(out_path / "metabook.json", 'w') as f:
        json.dump(metabook, f, indent=2)
    
    # Write individual lessons
    lessons_dir = out_path / "lessons"
    lessons_dir.mkdir(exist_ok=True)
    for lesson in lessons:
        with open(lessons_dir / f"{lesson.id}.json", 'w') as f:
            json.dump(asdict(lesson), f, indent=2)
    
    # Write topics
    topics_dir = out_path / "topics"
    topics_dir.mkdir(exist_ok=True)
    with open(topics_dir / "topic_metadata.json", 'w') as f:
        json.dump({name: asdict(t) for name, t in topics.items()}, f, indent=2)
    
    # Write summary stats
    stats = {
        "total_topics": len(topics),
        "total_lessons": len(lessons),
        "total_units": len(units),
        "pedagogy": {
            "ordering": "PageRank",
            "checkpoints": "Hub-based",
            "total_hub_checkpoints": len(hub_checkpoints)
        },
        "scale_distribution": {},
        "hub_topics": [t for t in topics if topics[t].hub_score > 0.5],
        "top_10_by_pagerank": [
            {"topic": t.name, "pagerank": round(t.pagerank, 4)}
            for t in sorted(topics.values(), key=lambda x: -x.pagerank)[:10]
        ],
        "top_10_hub_checkpoints": [
            {"topic": name, "hub_score": round(cp["hub_score"], 2), "total_degree": cp["total_degree"]}
            for name, cp in sorted(hub_checkpoints.items(), key=lambda x: -x[1]["hub_score"])[:10]
        ]
    }

    for scale in ["QUANTUM", "ELECTRONIC", "STRUCTURAL", "DESCRIPTIVE"]:
        stats["scale_distribution"][scale] = len([t for t in topics.values() if t.scale == scale])
    
    with open(out_path / "stats.json", 'w') as f:
        json.dump(stats, f, indent=2)
    
    print("\n" + "="*60)
    print("META-BOOK GENERATION COMPLETE")
    print("="*60)
    print(f"Topics:  {len(topics)}")
    print(f"Lessons: {len(lessons)}")
    print(f"Units:   {len(units)}")
    print(f"\nScale distribution:")
    for scale, count in stats["scale_distribution"].items():
        print(f"  {scale}: {count}")
    print(f"\nOutput: {output_dir}/")
    
    return metabook

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Meta-Book from Knowledge Graph")
    parser.add_argument("--kg", default="chemkg_enhanced.json",
                       help="Path to knowledge graph JSON")
    parser.add_argument("--output", default="meta-book",
                       help="Output directory")
    parser.add_argument("--stats", action="store_true",
                       help="Show statistics only")
    
    args = parser.parse_args()
    
    if args.stats:
        kg = load_knowledge_graph(args.kg)
        topics = extract_topics(kg)
        
        print(f"Topics: {len(topics)}")
        for scale in ["QUANTUM", "ELECTRONIC", "STRUCTURAL", "DESCRIPTIVE"]:
            count = len([t for t in topics.values() if t.scale == scale])
            print(f"  {scale}: {count}")
        
        print("\nTop 10 by PageRank:")
        by_pr = sorted(topics.values(), key=lambda x: -x.pagerank)[:10]
        for t in by_pr:
            print(f"  {t.name}: {t.pagerank:.4f} ({t.scale})")
        
        print("\nHub topics (score > 0.5):")
        hubs = [t for t in topics.values() if t.hub_score > 0.5]
        for t in sorted(hubs, key=lambda x: -x.hub_score)[:10]:
            print(f"  {t.name}: {t.hub_score:.2f}")
    else:
        generate_metabook(args.kg, args.output)
