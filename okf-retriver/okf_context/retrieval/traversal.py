from okf_context.exceptions import ErrorCode, OKFError
from okf_context.models import GraphNode


def traverse(index, concept_id: str, direction: str = "both", depth: int = 1, limit: int = 20) -> list[GraphNode]:
    if direction not in {"incoming", "outgoing", "both"}:
        raise OKFError("invalid direction")
    if depth < 0 or depth > 2:
        raise OKFError("invalid graph depth", ErrorCode.INVALID_GRAPH_DEPTH)
    if limit < 1:
        raise OKFError("invalid limit", ErrorCode.INVALID_LIMIT)
    frontier = {concept_id}
    seen = {concept_id}
    output: list[GraphNode] = []
    for distance in range(1, depth + 1):
        next_frontier = set()
        for node in sorted(frontier):
            targets = set()
            if direction in {"outgoing", "both"}:
                targets.update(index.outgoing.get(node, set()))
            if direction in {"incoming", "both"}:
                targets.update(index.incoming.get(node, set()))
            for target in sorted(targets):
                if target in seen:
                    continue
                seen.add(target)
                next_frontier.add(target)
                output.append(GraphNode(target, direction, distance))
                if len(output) >= limit:
                    return output
        frontier = next_frontier
    return output
