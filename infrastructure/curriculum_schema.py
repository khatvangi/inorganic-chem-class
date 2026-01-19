#!/usr/bin/env python3
"""
Chemistry Curriculum Infrastructure: Standardized Schema

defines the data structures for curriculum across all chemistry subfields.
all curriculum generators MUST produce output conforming to this schema.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from enum import Enum
import json


class Scale(Enum):
    """hierarchical knowledge scales - universal across chemistry"""
    QUANTUM = "QUANTUM"           # wave functions, orbitals, QM
    ELECTRONIC = "ELECTRONIC"     # electron config, bonding, MO theory
    STRUCTURAL = "STRUCTURAL"     # geometry, symmetry, crystal structure
    DESCRIPTIVE = "DESCRIPTIVE"   # properties, reactions, trends
    APPLICATION = "APPLICATION"   # industrial, biological, materials


class Level(Enum):
    """course levels for undergraduate chemistry"""
    INTRO = "100"      # freshman, gen chem
    FOUNDATION = "200" # sophomore, foundations
    CORE = "300"       # junior, major courses
    ADVANCED = "400"   # senior, advanced topics


@dataclass
class Source:
    """verified textbook source"""
    short_name: str          # e.g., "Atkins"
    pdf_name: str            # e.g., "Inorganic_Chemistry_Atkins_Shriver.pdf"
    chunk_count: int         # verified count from manifest
    best_for: List[str]      # topics this source excels at
    difficulty: str          # intro/intermediate/advanced
    rating: int              # 1-10 overall quality


@dataclass
class Topic:
    """single topic within a session"""
    name: str
    scale: Scale
    key_concepts: List[str]
    prerequisites: List[str] = field(default_factory=list)
    pagerank: float = 0.0    # centrality score if computed


@dataclass
class Session:
    """single class session (lecture)"""
    number: int
    title: str
    topics: List[Topic]
    learning_objectives: List[str]
    sources: Dict[str, str]  # role -> source short_name
    estimated_time: str = "50 min"


@dataclass
class Unit:
    """collection of sessions forming a unit"""
    number: int
    title: str
    description: str
    sessions: List[Session]
    primary_source: str      # main textbook for this unit
    secondary_sources: List[str]
    scale_focus: Scale       # dominant scale for this unit


@dataclass
class Curriculum:
    """complete curriculum for a chemistry subfield"""
    # metadata
    subfield: str            # e.g., "inorganic", "organic", "physical"
    course_code: str         # e.g., "CHEM 361"
    course_title: str
    level: Level
    credits: int

    # verified sources
    sources: List[Source]
    source_manifest: str     # path to verified_manifest.json

    # structure
    units: List[Unit]

    # computed metadata
    total_sessions: int = 0
    total_topics: int = 0
    scale_distribution: Dict[str, int] = field(default_factory=dict)

    # provenance
    generated_at: str = ""
    knowledge_graph: str = ""  # path to source graph
    methodology: str = ""

    def compute_metadata(self):
        """calculate derived fields"""
        self.total_sessions = sum(len(u.sessions) for u in self.units)
        self.total_topics = sum(
            len(t.topics) for u in self.units for t in u.sessions
        )

        # count scales
        scale_counts = {}
        for unit in self.units:
            for session in unit.sessions:
                for topic in session.topics:
                    s = topic.scale.value
                    scale_counts[s] = scale_counts.get(s, 0) + 1
        self.scale_distribution = scale_counts

    def to_dict(self) -> dict:
        """serialize to dict (for JSON)"""
        self.compute_metadata()
        d = asdict(self)
        # convert enums to strings
        for unit in d["units"]:
            unit["scale_focus"] = unit["scale_focus"].value if isinstance(unit["scale_focus"], Scale) else unit["scale_focus"]
            for session in unit["sessions"]:
                for topic in session["topics"]:
                    topic["scale"] = topic["scale"].value if isinstance(topic["scale"], Scale) else topic["scale"]
        d["level"] = d["level"].value if isinstance(d["level"], Level) else d["level"]
        for src in d["sources"]:
            pass  # sources don't have enums
        return d

    def to_json(self, path: str):
        """save to JSON file"""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def from_json(cls, path: str) -> 'Curriculum':
        """load from JSON file"""
        with open(path) as f:
            d = json.load(f)
        # would need to reconstruct objects - simplified for now
        return d  # returns dict, not full object


# source registry - maps short names to verified PDF names
# this is populated from verified_manifest.json
SOURCE_REGISTRY = {
    "inorganic": {
        "Atkins": "Inorganic_Chemistry_Atkins_Shriver.pdf",
        "Housecroft": "ic_tina.pdf",
        "Douglas": "descriptive_ic.pdf",
        "House": "descriptive_ic_house.pdf",
        "JD Lee": "concise_ic_jd_lee.pdf",
        "Basset": "ic_basset.pdf",
        "Advanced": "advancex_ic_applicaionts.pdf",
    },
    # future subfields will be added here
    "organic": {},
    "physical": {},
    "analytical": {},
    "biological": {},
    "materials": {},
}


def get_source_for_subfield(subfield: str, short_name: str) -> Optional[str]:
    """lookup PDF name from short name"""
    return SOURCE_REGISTRY.get(subfield, {}).get(short_name)


def validate_curriculum(curriculum: Curriculum) -> List[str]:
    """
    validate a curriculum against the schema.
    returns list of errors (empty if valid).
    """
    errors = []

    # check required fields
    if not curriculum.subfield:
        errors.append("Missing subfield")
    if not curriculum.course_code:
        errors.append("Missing course_code")
    if not curriculum.units:
        errors.append("No units defined")

    # check sources are verified
    verified_sources = set(SOURCE_REGISTRY.get(curriculum.subfield, {}).values())
    for src in curriculum.sources:
        if src.pdf_name not in verified_sources:
            errors.append(f"Unverified source: {src.pdf_name}")

    # check each unit
    for unit in curriculum.units:
        if not unit.sessions:
            errors.append(f"Unit {unit.number} has no sessions")
        for session in unit.sessions:
            if not session.topics:
                errors.append(f"Session {session.number} has no topics")
            if not session.learning_objectives:
                errors.append(f"Session {session.number} has no learning objectives")

    return errors


if __name__ == "__main__":
    # demo: print schema info
    print("Chemistry Curriculum Schema")
    print("="*40)
    print(f"\nScales: {[s.value for s in Scale]}")
    print(f"Levels: {[l.value for l in Level]}")
    print(f"\nRegistered subfields: {list(SOURCE_REGISTRY.keys())}")
    print(f"\nInorganic sources:")
    for short, pdf in SOURCE_REGISTRY["inorganic"].items():
        print(f"  {short:12} -> {pdf}")
