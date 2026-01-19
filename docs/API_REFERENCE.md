# API Reference

**CHEM 361 Knowledge Funnel API**

Base URL: `http://localhost:8361`

---

## Overview

The API provides access to the Knowledge Funnel system, enabling:
- Prerequisite tracing for any chemistry concept
- Concept listing and search
- Integration with external applications

---

## Endpoints

### 1. Trace Prerequisites

Traces all prerequisite concepts needed to understand a target concept.

```
GET /api/trace?q={question}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Natural language question or concept name |
| `max_depth` | int | No | Maximum prerequisite depth (default: 5) |

#### Example Request

```bash
curl "http://localhost:8361/api/trace?q=Why%20is%20copper%20sulfate%20blue"
```

#### Example Response

```json
{
  "target": "Crystal Field Theory",
  "target_info": {
    "label": "Crystal Field Theory",
    "type": "topic",
    "count": 165,
    "scale": "ELECTRONIC",
    "pagerank": 0.00166
  },
  "paths": [],
  "all_nodes": {
    "Crystal Field Theory": {
      "id": "Crystal Field Theory",
      "scale": "ELECTRONIC",
      "depth": 0,
      "count": 165,
      "pagerank": 0.00166,
      "is_target": true
    },
    "Molecular Orbital Theory": {
      "id": "Molecular Orbital Theory",
      "scale": "QUANTUM",
      "depth": 1,
      "count": 143,
      "pagerank": 0.00297,
      "is_target": false
    },
    "Atomic Orbitals": {
      "id": "Atomic Orbitals",
      "scale": "QUANTUM",
      "depth": 2,
      "count": 89,
      "pagerank": 0.00185,
      "is_target": false
    }
  },
  "all_edges": [
    {"source": "Molecular Orbital Theory", "target": "Crystal Field Theory"},
    {"source": "Atomic Orbitals", "target": "Molecular Orbital Theory"},
    {"source": "Point Group Symmetry", "target": "Crystal Field Theory"}
  ],
  "layers": {
    "QUANTUM": ["Molecular Orbital Theory", "Atomic Orbitals", "Electron Configuration"],
    "ELECTRONIC": ["Crystal Field Theory", "Spectroscopy Basics"],
    "STRUCTURAL": ["Point Group Symmetry", "Coordination Geometry"],
    "DESCRIPTIVE": ["Periodic Trends", "Ligand Properties"]
  }
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `target` | string | Matched concept name |
| `target_info` | object | Metadata about the target concept |
| `all_nodes` | object | Dictionary of all prerequisite nodes |
| `all_edges` | array | List of prerequisite relationships |
| `layers` | object | Nodes grouped by knowledge scale |

#### Node Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique concept identifier |
| `scale` | string | Knowledge scale (QUANTUM, ELECTRONIC, STRUCTURAL, DESCRIPTIVE) |
| `depth` | int | Distance from target (0 = target itself) |
| `count` | int | Mention count in textbooks |
| `pagerank` | float | Centrality score in knowledge graph |
| `is_target` | bool | Whether this is the target concept |

---

### 2. List Concepts

Returns all significant concepts in the knowledge graph.

```
GET /api/concepts
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `min_count` | int | No | Minimum mention count (default: 5) |
| `scale` | string | No | Filter by scale (QUANTUM, ELECTRONIC, STRUCTURAL, DESCRIPTIVE) |

#### Example Request

```bash
curl "http://localhost:8361/api/concepts?min_count=10&scale=ELECTRONIC"
```

#### Example Response

```json
{
  "count": 67,
  "concepts": [
    {
      "id": "Crystal Field Theory",
      "scale": "ELECTRONIC",
      "count": 165,
      "pagerank": 0.00166
    },
    {
      "id": "Molecular Orbital Theory",
      "scale": "QUANTUM",
      "count": 143,
      "pagerank": 0.00297
    }
  ]
}
```

---

### 3. Health Check

Returns server status and basic statistics.

```
GET /api/health
```

#### Example Request

```bash
curl "http://localhost:8361/api/health"
```

#### Example Response

```json
{
  "status": "ok",
  "nodes": 5374,
  "edges": 2885,
  "collections": {
    "textbooks_chunks": 8753
  }
}
```

---

### 4. Static Files

The server also serves static files for the visualizations.

| Path | Description |
|------|-------------|
| `/funnel.html` | Main funnel visualization |
| `/visualizations/` | Landing page with examples |
| `/visualizations/scales.html` | Scale-layered view |
| `/visualizations/hierarchy.html` | Radial/tree view |
| `/lectures/*.html` | Interactive lecture pages |

---

## Knowledge Scales

All concepts are classified into one of four scales:

| Scale | Color | Description | Examples |
|-------|-------|-------------|----------|
| `QUANTUM` | Red (#ef4444) | Wave functions, orbitals | Atomic orbitals, quantum numbers |
| `ELECTRONIC` | Purple (#8b5cf6) | Bonding, energy levels | Crystal field theory, MO theory |
| `STRUCTURAL` | Cyan (#06b6d4) | Geometry, symmetry | Point groups, coordination geometry |
| `DESCRIPTIVE` | Green (#22c55e) | Properties, trends | Periodic trends, reactivity |

---

## Error Responses

### 400 Bad Request

```json
{
  "error": "Missing required parameter: q"
}
```

### 404 Not Found

```json
{
  "error": "Concept not found: xyz"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error",
  "message": "Database connection failed"
}
```

---

## Rate Limits

Currently no rate limits are enforced for local development. For production deployment, consider:
- 100 requests/minute per IP
- 1000 requests/hour per IP

---

## CORS

The API allows cross-origin requests from any origin for development. For production:
- Restrict to `chem361.thebeakers.com`
- Add appropriate CORS headers

---

## Usage Examples

### JavaScript (Frontend)

```javascript
async function tracePrerequisites(question) {
    const response = await fetch(
        `/api/trace?q=${encodeURIComponent(question)}`
    );
    const data = await response.json();

    console.log(`Target: ${data.target}`);
    console.log(`Prerequisites: ${Object.keys(data.all_nodes).length}`);
    console.log(`Edges: ${data.all_edges.length}`);

    // Group by scale
    for (const [scale, concepts] of Object.entries(data.layers)) {
        console.log(`${scale}: ${concepts.length} concepts`);
    }

    return data;
}

// Usage
tracePrerequisites("Why is copper sulfate blue?");
```

### Python

```python
import requests

def trace_prerequisites(question, base_url="http://localhost:8361"):
    response = requests.get(
        f"{base_url}/api/trace",
        params={"q": question}
    )
    response.raise_for_status()
    return response.json()

# Usage
data = trace_prerequisites("crystal field theory")
print(f"Target: {data['target']}")
print(f"QUANTUM prerequisites: {data['layers']['QUANTUM']}")
```

### cURL

```bash
# Trace prerequisites
curl -s "http://localhost:8361/api/trace?q=magnetism" | jq '.layers'

# List concepts
curl -s "http://localhost:8361/api/concepts?min_count=50" | jq '.concepts[].id'

# Health check
curl -s "http://localhost:8361/api/health" | jq '.'
```

---

## Integration with RAG System

The API can be combined with the RAG system for content retrieval:

```python
import requests

# 1. Get prerequisites for a topic
prereqs = requests.get(
    "http://localhost:8361/api/trace",
    params={"q": "crystal field theory"}
).json()

# 2. Use RAG to get content for each prerequisite
from qdrant_client import QdrantClient
from lecture_qa_generator import embed_query

qdrant = QdrantClient("http://localhost:6333")

for concept in prereqs["layers"]["QUANTUM"]:
    vector = embed_query(concept)
    chunks = qdrant.query_points(
        collection_name="textbooks_chunks",
        query=vector,
        using="dense",
        limit=5
    )
    print(f"{concept}: {len(chunks.points)} chunks found")
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-18 | Initial release with trace, concepts, health endpoints |

---

*API documentation for CHEM 361 Knowledge Funnel System*
