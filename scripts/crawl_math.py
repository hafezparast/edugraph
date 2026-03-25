"""
Crawl educational sources and extract knowledge graph data using crawl4ai.

Usage:
    pip install -r requirements.txt
    crawl4ai-setup
    export OPENAI_API_KEY=your_key   # or any LiteLLM-supported provider
    python crawl_math.py
"""

import asyncio
import json
import os
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy


# --- Pydantic models matching our data schema ---

class Node(BaseModel):
    id: str
    label: str
    type: str
    description: str
    grade_range: List[str] = []
    tags: List[str] = []
    sources: List[str] = []


class Edge(BaseModel):
    source: str
    target: str
    relation: str
    description: Optional[str] = None


class KnowledgeChunk(BaseModel):
    """What the LLM extracts from each page."""
    nodes: List[Node]
    edges: List[Edge]


# --- Configuration ---

DATA_DIR = Path(__file__).parent.parent / "data"

# Sources to crawl — add more URLs here
SOURCES = [
    "https://en.wikipedia.org/wiki/Mathematics",
    "https://en.wikipedia.org/wiki/Areas_of_mathematics",
    "https://en.wikipedia.org/wiki/Algebra",
    "https://en.wikipedia.org/wiki/Geometry",
    "https://en.wikipedia.org/wiki/Calculus",
    "https://en.wikipedia.org/wiki/Linear_algebra",
    "https://en.wikipedia.org/wiki/Number_theory",
    "https://en.wikipedia.org/wiki/Topology",
    "https://en.wikipedia.org/wiki/Abstract_algebra",
    "https://en.wikipedia.org/wiki/Real_analysis",
    "https://en.wikipedia.org/wiki/Statistics",
]

EXTRACTION_INSTRUCTION = """
Extract mathematical concepts, theorems, axioms, definitions, and their relationships
from this educational content. For each concept:

1. Create a node with:
   - id: hierarchical dot-notation (e.g., "math.algebra.quadratic_formula")
   - label: human-readable name
   - type: one of "domain", "branch", "topic", "concept", "axiom", "theorem", "definition", "formula", "technique", "question", "example"
   - description: clear, concise explanation
   - grade_range: approximate education levels (K, 1-12, undergraduate, graduate, PhD)
   - tags: relevant keywords

2. Create edges between related concepts with:
   - relation: one of "contains", "prerequisite_for", "builds_on", "related_to",
     "generalizes", "specializes", "proves", "applies", "example_of",
     "formalized_by", "equivalent_to"

Focus on creating a rich web of prerequisite and structural relationships.
"""

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "openai/gpt-4o-mini")
LLM_API_KEY = os.environ.get("OPENAI_API_KEY", "")


async def crawl_and_extract(urls: list[str]) -> KnowledgeChunk:
    """Crawl URLs and extract knowledge graph data."""
    strategy = LLMExtractionStrategy(
        llm_config={"provider": LLM_PROVIDER, "api_token": LLM_API_KEY},
        schema=KnowledgeChunk.model_json_schema(),
        extraction_type="schema",
        instruction=EXTRACTION_INSTRUCTION,
        chunk_token_threshold=2000,
        overlap_rate=0.1,
        input_format="fit_markdown",
    )

    config = CrawlerRunConfig(extraction_strategy=strategy)
    browser_config = BrowserConfig(headless=True)

    all_nodes = []
    all_edges = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for url in urls:
            print(f"Crawling: {url}")
            try:
                result = await crawler.arun(url=url, config=config)
                if result.success and result.extracted_content:
                    chunks = json.loads(result.extracted_content)
                    for chunk in chunks if isinstance(chunks, list) else [chunks]:
                        if "nodes" in chunk:
                            all_nodes.extend(chunk["nodes"])
                        if "edges" in chunk:
                            all_edges.extend(chunk["edges"])
                    print(f"  Extracted {len(chunks) if isinstance(chunks, list) else 1} chunk(s)")
                else:
                    print(f"  Failed: {result.error_message if hasattr(result, 'error_message') else 'unknown error'}")
            except Exception as e:
                print(f"  Error: {e}")

    return KnowledgeChunk(nodes=all_nodes, edges=all_edges)


def merge_into_existing(new_data: KnowledgeChunk, filepath: Path):
    """Merge newly extracted data into the existing JSON data file."""
    with open(filepath) as f:
        existing = json.load(f)

    existing_node_ids = {n["id"] for n in existing["nodes"]}
    existing_edge_keys = {(e["source"], e["target"], e["relation"]) for e in existing["edges"]}

    added_nodes = 0
    for node in new_data.nodes:
        if node.id not in existing_node_ids:
            existing["nodes"].append(node.model_dump())
            existing_node_ids.add(node.id)
            added_nodes += 1

    added_edges = 0
    for edge in new_data.edges:
        key = (edge.source, edge.target, edge.relation)
        # Only add edges where both nodes exist
        if key not in existing_edge_keys and edge.source in existing_node_ids and edge.target in existing_node_ids:
            existing["edges"].append(edge.model_dump(exclude_none=True))
            existing_edge_keys.add(key)
            added_edges += 1

    existing["metadata"]["last_updated"] = "2026-03-25"
    existing["metadata"]["version"] = _bump_patch(existing["metadata"]["version"])

    with open(filepath, "w") as f:
        json.dump(existing, f, indent=2)

    print(f"\nMerged: +{added_nodes} nodes, +{added_edges} edges")
    print(f"Total: {len(existing['nodes'])} nodes, {len(existing['edges'])} edges")


def _bump_patch(version: str) -> str:
    parts = version.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)


async def main():
    if not LLM_API_KEY:
        print("Set OPENAI_API_KEY (or your LLM provider's key) to run extraction.")
        print("Example: export OPENAI_API_KEY=sk-...")
        return

    data_file = DATA_DIR / "mathematics.json"
    new_data = await crawl_and_extract(SOURCES)
    merge_into_existing(new_data, data_file)


if __name__ == "__main__":
    asyncio.run(main())
