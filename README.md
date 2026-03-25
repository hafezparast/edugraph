# EduGraph

Interactive knowledge graph for education — mapping concepts, theorems, axioms, and their connections from kindergarten through PhD level.

**[Live Demo →](https://hafezparast.github.io/edugraph/)**

## What is this?

A static, open-source knowledge graph that breaks down educational domains (starting with mathematics) into their fundamental building blocks and maps the relationships between them.

- **Nodes**: Concepts, theorems, axioms, definitions, formulas, techniques
- **Edges**: Prerequisites, generalizations, proofs, applications, containment
- **Grade levels**: Tagged from K through PhD

All data is stored as flat JSON files — no backend needed. The frontend reads the JSON and renders an interactive graph you can explore, search, and filter.

## Data Format

Each domain has a JSON file in `/data/` following this structure:

```json
{
  "metadata": { "domain": "mathematics", "version": "0.1.0" },
  "nodes": [
    {
      "id": "math.algebra.quadratic_formula",
      "label": "Quadratic Formula",
      "type": "formula",
      "description": "x = (-b ± √(b²-4ac)) / 2a",
      "grade_range": ["9", "10"],
      "tags": ["algebra"]
    }
  ],
  "edges": [
    {
      "source": "math.algebra.quadratic_equations",
      "target": "math.algebra.quadratic_formula",
      "relation": "formalized_by"
    }
  ]
}
```

See `data/schema.json` for the full specification.

### Node Types
`domain` · `branch` · `topic` · `concept` · `axiom` · `theorem` · `definition` · `formula` · `technique` · `question` · `example`

### Edge Relations
`contains` · `prerequisite_for` · `builds_on` · `related_to` · `generalizes` · `specializes` · `proves` · `applies` · `example_of` · `formalized_by` · `equivalent_to`

## Contributing

Add nodes and edges to the JSON files in `/data/`. The schema enforces consistency. PRs welcome — especially for:

- Expanding coverage of existing branches
- Adding new domains (physics, computer science, etc.)
- Fixing inaccuracies in descriptions or relationships
- Adding grade-level tags

## Enrichment Scripts

The `/scripts/` directory contains Python scripts using [crawl4ai](https://github.com/unclecode/crawl4ai) to automatically extract and enrich graph data from educational sources.

```bash
cd scripts
pip install -r requirements.txt
crawl4ai-setup
export OPENAI_API_KEY=your_key
python crawl_math.py
```

## License

MIT
