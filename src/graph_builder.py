
from collections import defaultdict, deque


def find_path(graph, start, target):
    """Return one directed path from start to target, if one exists."""
    adjacency = defaultdict(list)

    for source, destination in graph:
        adjacency[source].append(destination)

    queue = deque([(start, [start])])
    visited = {start}

    while queue:
        node, path = queue.popleft()

        if node == target:
            return path

        for neighbor in adjacency[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return None


def compare_graphs(old_graph, new_graph):
    old_edges = set(old_graph)
    new_edges = set(new_graph)

    return {
        "added_edges": sorted(new_edges - old_edges),
        "removed_edges": sorted(old_edges - new_edges),
    }


if __name__ == "__main__":
    # Synthetic example for testing graph comparison.
    old_graph = [
        ("Developer", "ReadOnlyRole"),
        ("ReadOnlyRole", "ReadS3"),
    ]

    new_graph = old_graph + [
        ("Developer", "AdminRole"),
        ("AdminRole", "AdminAccess"),
    ]

    result = compare_graphs(old_graph, new_graph)

    print("Added relationships:")
    for source, destination in result["added_edges"]:
        print(f"  {source} -> {destination}")

    print("\nNewly possible path:")
    path = find_path(new_graph, "Developer", "AdminAccess")
    old_path = find_path(old_graph, "Developer", "AdminAccess")

    if path and not old_path:
        print("  " + " -> ".join(path))
    else:
        print("  No new path detected.")
