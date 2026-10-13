---
title: Recuperador de contexto OKF
description: Recuperador determinista y generador de respuestas fundamentadas en varios documentos Markdown OKF.
type: project-documentation
tags: [okf, retrieval, reasoning, python]
---

# Recuperador de contexto OKF

Recuperador determinista para corpus Markdown OKF. El corpus es la fuente de
verdad; el índice se reconstruye en memoria y no requiere LangChain, LangGraph,
embeddings ni una base de datos externa.

## Plugin para agentes

Este repositorio también incluye el skill `okf-graph-retrieval` para Codex y
Claude Code. Recorre un grafo de enlaces OKF y devuelve secciones Markdown con
la procedencia exacta (`path` y `section_id`).

Instalación desde el marketplace de GitHub:

```bash
codex plugin marketplace add jdvacasf/okf-retriever
codex plugin add okf-graph-retrieval@okf-retriver
```

Claude Code:

```text
/plugin marketplace add jdvacasf/okf-retriever
/plugin install okf-graph-retrieval@okf-retriver
```

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

`create_okf_tools(retriever)` devuelve un registro de siete objetos `ToolSpec`,
indexados por nombre. Cada schema declara parámetros y valida la entrada antes
de delegar en el mismo retriever.

## Tools públicas

| Tool | Parámetros principales | Uso |
|---|---|---|
| `search_okf_context` | `query`, `types`, `tags`, `status`, `path_prefix`, `limit` | Busca conceptos relevantes con puntuación, términos coincidentes, fragmento y procedencia. |
| `search_okf_sections` | `query`, `path_prefix`, `concept_ids`, `limit` | Busca secciones Markdown concretas sin devolver documentos completos. |
| `browse_okf` | `path`, `depth` | Explora conceptos y directorios indexados bajo una ruta. |
| `inspect_okf_concept` | `concept_id` | Devuelve los metadatos, las secciones y los enlaces de un concepto. |
| `read_okf_section` | `section_id` | Lee una sección exacta; un ID desconocido devuelve `SECTION_NOT_FOUND`. |
| `traverse_okf_graph` | `concept_id`, `direction`, `depth`, `limit` | Recorre enlaces `incoming`, `outgoing` o `both` respetando los límites configurados. |
| `get_okf_context` | `query`, `max_tokens`, `max_sections` | Construye contexto deduplicado y limitado por número de tokens. |

Ejemplo:

```python
search_okf_context = tools["search_okf_context"]
results = search_okf_context(query="authentication", limit=5)

get_okf_context = tools["get_okf_context"]
context = get_okf_context(query="authentication", max_tokens=400)
```

La salida conserva la procedencia (`concept_id`, `path`, `section_id` o
`heading_path`), y las operaciones respetan el orden determinista del índice.
La información de calidad está disponible mediante
`index.quality_report.to_dict()`; incluye documentos rechazados, diagnósticos,
enlaces rotos y duración, sin incluir cuerpos documentales ni rutas absolutas.

## Respuestas fundamentadas en varios documentos

`MultiDocumentAnswerer` usa el contexto deduplicado y limitado del retriever,
pero mantiene el proveedor LLM fuera del núcleo. El proveedor implementa un
único método `answer(request)` y devuelve el mapping definido por el contrato:

```python
from okf_context.reasoning import MultiDocumentAnswerer


class Provider:
    def answer(self, request):
        section = request.evidence[0]
        return {
            "answer": "Respuesta fundamentada en el corpus.",
            "synthesis": "Síntesis breve de la evidencia citada.",
            "citations": [{"path": section.path, "section_id": section.section_id}],
            "insufficient": False,
            "conflicts": [],
        }


answerer = MultiDocumentAnswerer(retriever, Provider())
result = answerer.answer("¿Qué dice el corpus?", max_tokens=800, max_sections=8)
print(result.to_dict())
```

Las citas solo se aceptan si `path` y `section_id` coinciden exactamente con el
contexto utilizado. Si no hay evidencia, el answerer devuelve un
`GroundedAnswer` con `insufficient=True` sin llamar al proveedor. Los errores
operativos usan códigos estables:

- `PROVIDER_NOT_CONFIGURED`: no hay ningún proveedor configurado.
- `PROVIDER_FAILURE`: el proveedor ha fallado.
- `INVALID_PROVIDER_OUTPUT`: el mapping, las citas o los conflictos no cumplen
  el contrato.

Las instrucciones fijas y el texto de evidencia se envían por separado. Los
logs de razonamiento solo contienen el resultado operativo y el tiempo
transcurrido; no incluyen preguntas, evidencia ni respuestas.

## Validación

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m compileall -q okf_context tests
```
