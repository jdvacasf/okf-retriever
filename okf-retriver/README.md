---
title: OKF Context Retriever
description: Deterministic retriever and grounded multi-document answerer for OKF Markdown corpora.
type: project-documentation
tags: [okf, retrieval, reasoning, python]
---

# OKF Context Retriever

Deterministic retriever for OKF Markdown corpora. The corpus is the source of
truth; the index is rebuilt in memory and requires no LangChain, LangGraph,
embeddings, or external database.

## Agent plugin

This repository also packages the `okf-graph-retrieval` skill for Codex and
Claude Code. It traverses an OKF link graph and returns Markdown sections with
exact `path` and `section_id` provenance.

Install from the GitHub marketplace:

```bash
codex plugin marketplace add jdvacasf/okf-retriever
codex plugin add okf-graph-retrieval@okf-retriver
```

Claude Code:

```text
/plugin marketplace add jdvacasf/okf-retriever
/plugin install okf-graph-retrieval@okf-retriver
```

## Create the retriever

```python
from pathlib import Path

from okf_context import OKFContextConfig, OKFContextIndex, OKFRetriever
from okf_context.tools import create_okf_tools

config = OKFContextConfig(graph_root=Path("tests/fixtures/okf"))
index = OKFContextIndex.build(config)
retriever = OKFRetriever(index, config)
tools = create_okf_tools(retriever)
```

`create_okf_tools(retriever)` returns a registry of seven `ToolSpec` objects,
indexed by name. Each schema declares parameters and validates input before
delegating to the same retriever.

## Public tools

| Tool | Main parameters | Purpose |
|---|---|---|
| `search_okf_context` | `query`, `types`, `tags`, `status`, `path_prefix`, `limit` | Finds relevant concepts with scores, matched terms, snippets, and provenance. |
| `search_okf_sections` | `query`, `path_prefix`, `concept_ids`, `limit` | Finds specific Markdown sections without returning entire documents. |
| `browse_okf` | `path`, `depth` | Explores concepts and indexed directories under a path. |
| `inspect_okf_concept` | `concept_id` | Returns a concept's metadata, sections, and links. |
| `read_okf_section` | `section_id` | Reads an exact section; an unknown ID returns `SECTION_NOT_FOUND`. |
| `traverse_okf_graph` | `concept_id`, `direction`, `depth`, `limit` | Traverses `incoming`, `outgoing`, or `both` links within configured limits. |
| `get_okf_context` | `query`, `max_tokens`, `max_sections` | Builds deduplicated context bounded by token count. |

Example:

```python
search_okf_context = tools["search_okf_context"]
results = search_okf_context(query="authentication", limit=5)

get_okf_context = tools["get_okf_context"]
context = get_okf_context(query="authentication", max_tokens=400)
```

The output preserves provenance (`concept_id`, `path`, `section_id`, or
`heading_path`), and operations follow the index's deterministic order.
Quality information is available through `index.quality_report.to_dict()`; it
includes rejected documents, diagnostics, broken links, and duration without
including document bodies or absolute paths.

## Grounded answers across multiple documents

`MultiDocumentAnswerer` uses deduplicated, bounded context from the retriever
while keeping the LLM provider outside the core. The provider implements a
single `answer(request)` method and returns the mapping described by the
contract:

```python
from okf_context.reasoning import MultiDocumentAnswerer


class Provider:
    def answer(self, request):
        section = request.evidence[0]
        return {
            "answer": "An answer supported by the corpus.",
            "synthesis": "A brief synthesis of the cited evidence.",
            "citations": [{"path": section.path, "section_id": section.section_id}],
            "insufficient": False,
            "conflicts": [],
        }


answerer = MultiDocumentAnswerer(retriever, Provider())
result = answerer.answer("What does the corpus say?", max_tokens=800, max_sections=8)
print(result.to_dict())
```

Citations are accepted only when their `path` and `section_id` exactly match
the context used. If there is no evidence, the answerer returns a
`GroundedAnswer` with `insufficient=True` without calling the provider.
Operational failures use stable codes:

- `PROVIDER_NOT_CONFIGURED`: no provider is configured.
- `PROVIDER_FAILURE`: the provider failed.
- `INVALID_PROVIDER_OUTPUT`: the mapping, citations, or conflicts do not meet
  the contract.

Fixed instructions and evidence text are passed separately. Reasoning logs
contain only the operational outcome and elapsed time; they do not include
questions, evidence, or answers.

## Validation

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m compileall -q okf_context tests
```
