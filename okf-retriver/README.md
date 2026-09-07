# OKF Context Retriever

Retriever determinista para corpus OKF en Markdown. El corpus es la fuente de
verdad; el índice se reconstruye en memoria y no requiere LangChain, LangGraph,
embeddings ni una base de datos externa.

## Crear el retriever

```python
from pathlib import Path

from okf_context import OKFContextConfig, OKFContextIndex, OKFRetriever
from okf_context.tools import create_okf_tools

config = OKFContextConfig(graph_root=Path("tests/fixtures/okf"))
index = OKFContextIndex.build(config)
retriever = OKFRetriever(index, config)
tools = create_okf_tools(retriever)
```

`create_okf_tools(retriever)` devuelve siete callables preparados para ser
registrados en un runtime de agentes. Cada tool delega en el mismo retriever y
devuelve los mismos resultados y errores que la API directa.

## Tools públicas

| Tool | Parámetros principales | Uso |
|---|---|---|
| `search_okf_context` | `query`, `types`, `tags`, `status`, `path_prefix`, `limit` | Busca conceptos relevantes con score, términos coincidentes, snippet y provenance. |
| `search_okf_sections` | `query`, `path_prefix`, `concept_ids`, `limit` | Busca fragmentos Markdown concretos sin devolver documentos completos. |
| `browse_okf` | `path`, `depth` | Explora conceptos y directorios indexados bajo una ruta. |
| `inspect_okf_concept` | `concept_id` | Devuelve metadata, secciones y enlaces de un concepto. |
| `read_okf_section` | `section_id` | Lee una sección exacta; un ID inexistente produce `SECTION_NOT_FOUND`. |
| `traverse_okf_graph` | `concept_id`, `direction`, `depth`, `limit` | Recorre enlaces `incoming`, `outgoing` o `both` con límites. |
| `get_okf_context` | `query`, `max_tokens`, `max_sections` | Ensambla contexto deduplicado y acotado por tokens. |

Ejemplo de invocación:

```python
search_okf_context = tools[0]
results = search_okf_context(query="authentication", limit=5)

get_okf_context = tools[6]
context = get_okf_context(query="authentication", max_tokens=400)
```

La salida mantiene la procedencia (`concept_id`, `path`, `section_id` o
`heading_path`) y las operaciones respetan el orden determinista del índice.

## Validación

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m compileall -q okf_context tests
```
