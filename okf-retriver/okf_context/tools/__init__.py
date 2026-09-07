import re
from typing import Any, Callable

from okf_context.exceptions import ToolInputError
from okf_context.models import ParameterSpec, ToolSpec


def _validated(name: str, description: str, retriever: Any, fn: Callable[..., Any], parameters: tuple[ParameterSpec, ...]) -> ToolSpec:
    expected = {parameter.name: parameter for parameter in parameters}

    def invoke(**kwargs: Any) -> Any:
        for key in kwargs:
            if key not in expected:
                raise ToolInputError(name, key, "unknown argument")
        values = dict(kwargs)
        for key, parameter in expected.items():
            if key not in values:
                if parameter.required:
                    raise ToolInputError(name, key, "missing argument")
                values[key] = parameter.default
            value = values[key]
            if value is not None and parameter.type_name == "string" and not isinstance(value, str):
                raise ToolInputError(name, key, "expected string")
            if key == "query" and value is not None and (not value.strip() or not re.search(r"[\wÀ-ÿ]", value)):
                raise ToolInputError(name, key, "must contain a searchable token")
            if value is not None and parameter.type_name == "integer" and (not isinstance(value, int) or isinstance(value, bool)):
                raise ToolInputError(name, key, "expected integer")
            if value is not None and parameter.type_name == "list[string]" and (not isinstance(value, list) or not all(isinstance(item, str) for item in value)):
                raise ToolInputError(name, key, "expected list[string]")
            if parameter.minimum is not None and value is not None and value < parameter.minimum:
                raise ToolInputError(name, key, f"must be >= {parameter.minimum}")
            maximums = {
                "limit": retriever.config.max_graph_results if name == "traverse_okf_graph" else retriever.config.max_search_limit,
                "depth": retriever.config.max_graph_depth,
                "max_tokens": retriever.config.max_context_tokens,
                "max_sections": retriever.config.max_search_limit,
            }
            if key in maximums and value is not None and value > maximums[key]:
                raise ToolInputError(name, key, f"must be <= {maximums[key]}")
            if parameter.choices and value is not None and value not in parameter.choices:
                raise ToolInputError(name, key, f"must be one of {parameter.choices}")
        return fn(retriever, **values)

    return ToolSpec(name, description, parameters, invoke)


def create_okf_tools(retriever) -> dict[str, ToolSpec]:
    return {tool.name: tool for tool in (search_okf_context(retriever), search_okf_sections(retriever), browse_okf(retriever), inspect_okf_concept(retriever), read_okf_section(retriever), traverse_okf_graph(retriever), get_okf_context(retriever))}


def search_okf_context(retriever):
    from .search_context import call
    return _validated("search_okf_context", "Search indexed OKF concepts.", retriever, call, (ParameterSpec("query", "string", True), ParameterSpec("types", "list[string]"), ParameterSpec("tags", "list[string]"), ParameterSpec("status", "list[string]"), ParameterSpec("path_prefix", "string"), ParameterSpec("limit", "integer", minimum=1)))


def search_okf_sections(retriever):
    from .search_sections import call
    return _validated("search_okf_sections", "Search indexed OKF sections.", retriever, call, (ParameterSpec("query", "string", True), ParameterSpec("path_prefix", "string"), ParameterSpec("concept_ids", "list[string]"), ParameterSpec("limit", "integer", minimum=1)))


def browse_okf(retriever):
    from .browse import call
    return _validated("browse_okf", "Browse indexed OKF paths.", retriever, call, (ParameterSpec("path", "string", default=""), ParameterSpec("depth", "integer", default=1, minimum=1)))


def inspect_okf_concept(retriever):
    from .inspect_concept import call
    return _validated("inspect_okf_concept", "Inspect one OKF concept.", retriever, call, (ParameterSpec("concept_id", "string", True),))


def read_okf_section(retriever):
    from .read_section import call
    return _validated("read_okf_section", "Read one OKF section.", retriever, call, (ParameterSpec("section_id", "string", True),))


def traverse_okf_graph(retriever):
    from .traverse_graph import call
    return _validated("traverse_okf_graph", "Traverse the OKF graph.", retriever, call, (ParameterSpec("concept_id", "string", True), ParameterSpec("direction", "string", default="both", choices=("outgoing", "incoming", "both")), ParameterSpec("depth", "integer", default=1, minimum=1), ParameterSpec("limit", "integer", default=20, minimum=1)))


def get_okf_context(retriever):
    from .get_context import call
    return _validated("get_okf_context", "Build a bounded context package.", retriever, call, (ParameterSpec("query", "string", True), ParameterSpec("max_tokens", "integer", minimum=1), ParameterSpec("max_sections", "integer", default=8, minimum=1)))
