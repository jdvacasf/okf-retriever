from okf_context.models import OKFConcept


def add_relationships(index, concept: OKFConcept) -> None:
    index.outgoing.setdefault(concept.concept_id, set()).update(concept.outgoing_links)
    for target in concept.outgoing_links:
        index.incoming.setdefault(target, set()).add(concept.concept_id)
