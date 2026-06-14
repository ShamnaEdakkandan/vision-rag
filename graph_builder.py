import json
import re
from collections import Counter
from pathlib import Path

STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this",
    "page", "pages", "table", "tables", "chart", "charts",
    "image", "images", "diagram", "diagrams", "document",
    "page", "shown", "show", "include", "includes", "information",
    "using", "used", "also", "data", "text", "visual",
}


def extract_concepts(text, max_concepts=12):
    if not text:
        return []

    tokens = re.findall(r"[a-zA-Z]{4,}", text.lower())
    filtered = [token for token in tokens if token not in STOPWORDS]
    counts = Counter(filtered)
    return [word for word, _ in counts.most_common(max_concepts)]


def build_graph(page_metadata, graph_path=None, min_overlap=2):
    graph_path = Path(graph_path or "index/graph.json")
    graph_path.parent.mkdir(parents=True, exist_ok=True)

    nodes = {}
    for page_path, metadata in page_metadata.items():
        nodes[page_path] = {
            "document": metadata.get("document"),
            "page_number": metadata.get("page_number"),
            "concepts": extract_concepts(metadata.get("description", "")),
        }

    edges = {}
    page_paths = list(nodes.keys())

    for i in range(len(page_paths)):
        for j in range(i + 1, len(page_paths)):
            p1 = page_paths[i]
            p2 = page_paths[j]
            overlap = set(nodes[p1]["concepts"]) & set(nodes[p2]["concepts"])
            if len(overlap) >= min_overlap:
                edges.setdefault(p1, {})[p2] = len(overlap)
                edges.setdefault(p2, {})[p1] = len(overlap)

    graph = {"nodes": nodes, "edges": edges}

    with open(graph_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)

    return graph


def load_graph(graph_path=None):
    graph_path = Path(graph_path or "index/graph.json")
    if not graph_path.exists():
        return {"nodes": {}, "edges": {}}
    with open(graph_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_graph_neighbors(page_paths, graph_path=None, max_neighbors=2):
    graph = load_graph(graph_path)
    neighbors = []
    seen = set(page_paths)

    for page_path in page_paths:
        edges = graph.get("edges", {}).get(page_path, {})
        for neighbor_path, weight in sorted(edges.items(), key=lambda item: item[1], reverse=True):
            if neighbor_path not in seen and neighbor_path not in neighbors:
                neighbors.append(neighbor_path)
                seen.add(neighbor_path)
                if len(neighbors) >= max_neighbors:
                    break
        if len(neighbors) >= max_neighbors:
            break

    return neighbors
