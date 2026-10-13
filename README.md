# OKF Context Retriever

Deterministic, filesystem-backed retrieval for Open Knowledge Format documents.

Core package uses the OKF filesystem as source of truth, builds an in-memory
index, searches concepts and sections, traverses links, and assembles bounded
context with provenance. No vector database, embeddings, or LangGraph dependency
is required.

## Install the agent plugin

The plugin package is in `okf-retriver/`; the marketplace catalog is at the
repository root.

```bash
codex plugin marketplace add jdvacasf/okf-retriever
codex plugin add okf-graph-retrieval@okf-retriver
```

For Claude Code:

```text
/plugin marketplace add jdvacasf/okf-retriever
/plugin install okf-graph-retrieval@okf-retriver
```

```python
from pathlib import Path
from okf_context import OKFContextConfig, OKFContextIndex, OKFRetriever

config = OKFContextConfig(graph_root=Path("knowledge"))
retriever = OKFRetriever(OKFContextIndex.build(config), config)
context = retriever.get_context("authentication deployment")
```

Run available tests with:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```
