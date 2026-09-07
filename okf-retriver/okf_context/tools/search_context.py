def call(retriever, **kwargs):
    return retriever.search_context(**kwargs)
