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

`create_okf_tools(retriever)` devuelve un registro de siete `ToolSpec` indexado
por nombre. Cada schema declara parámetros y valida la entrada antes de
delegar en el mismo retriever.

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
search_okf_context = tools["search_okf_context"]
results = search_okf_context(query="authentication", limit=5)

get_okf_context = tools["get_okf_context"]
context = get_okf_context(query="authentication", max_tokens=400)
```

La salida mantiene la procedencia (`concept_id`, `path`, `section_id` o
`heading_path`) y las operaciones respetan el orden determinista del índice.
El estado de calidad está disponible como `index.quality_report.to_dict()`;
incluye documentos rechazados, diagnósticos, enlaces rotos y duración, sin
incluir cuerpos documentales ni rutas absolutas.

## Respuestas fundamentadas en varios documentos

`MultiDocumentAnswerer` usa el contexto deduplicado y acotado del retriever,
pero mantiene el proveedor LLM fuera del núcleo. El proveedor implementa un
único método `answer(request)` y devuelve el mapping descrito por el contrato:

```python
from okf_context.reasoning import MultiDocumentAnswerer


class Provider:
    def answer(self, request):
        section = request.evidence[0]
        return {
            "answer": "Respuesta soportada por el corpus.",
            "synthesis": "Síntesis breve de la evidencia citada.",
            "citations": [{"path": section.path, "section_id": section.section_id}],
            "insufficient": False,
            "conflicts": [],
        }


answerer = MultiDocumentAnswerer(retriever, Provider())
result = answerer.answer("¿Qué dice el corpus?", max_tokens=800, max_sections=8)
print(result.to_dict())
```

Las citas solo se aceptan si coinciden exactamente con el `path` y
`section_id` del contexto usado. Sin evidencia se devuelve un
`GroundedAnswer` con `insufficient=True` sin llamar al proveedor. Los fallos
operativos usan códigos estables:

- `PROVIDER_NOT_CONFIGURED`: falta el proveedor.
- `PROVIDER_FAILURE`: el proveedor falló.
- `INVALID_PROVIDER_OUTPUT`: el mapping, las citas o los conflictos no cumplen
  el contrato.

Las instrucciones fijas y el texto de evidencia viajan separados. Los logs de
razonamiento solo contienen el resultado operativo y el tiempo transcurrido;
no incluyen preguntas, evidencia ni respuestas.

## Validación

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m compileall -q okf_context tests
```
