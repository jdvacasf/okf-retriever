def create_okf_tools(retriever):
    return [
        search_okf_context(retriever), search_okf_sections(retriever), browse_okf(retriever),
        inspect_okf_concept(retriever), read_okf_section(retriever),
        traverse_okf_graph(retriever), get_okf_context(retriever),
    ]


def _adapter(name, fn, retriever):
    def tool(**kwargs):
        return fn(retriever, **kwargs)
    tool.__name__ = name
    tool.__doc__ = name
    return tool


def search_okf_context(retriever):
    from .search_context import call
    return _adapter("search_okf_context", call, retriever)


def search_okf_sections(retriever):
    from .search_sections import call
    return _adapter("search_okf_sections", call, retriever)


def browse_okf(retriever):
    from .browse import call
    return _adapter("browse_okf", call, retriever)


def inspect_okf_concept(retriever):
    from .inspect_concept import call
    return _adapter("inspect_okf_concept", call, retriever)


def read_okf_section(retriever):
    from .read_section import call
    return _adapter("read_okf_section", call, retriever)


def traverse_okf_graph(retriever):
    from .traverse_graph import call
    return _adapter("traverse_okf_graph", call, retriever)


def get_okf_context(retriever):
    from .get_context import call
    return _adapter("get_okf_context", call, retriever)
