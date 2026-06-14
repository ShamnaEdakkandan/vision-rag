from pathlib import Path

from PIL import Image
from qdrant_client import QdrantClient

from rag import client
from graph_builder import get_graph_neighbors, load_graph


def describe_query_image(image):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            image,
            """
            Describe this image as a query input for a PDF search.
            Summarize the visual content, charts, tables, diagrams, and text.
            Keep the description concise and searchable.
            """
        ]
    )
    return response.text


def embed_text(text):
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    return response.embeddings[0].values


def retrieve_pages(
    question,
    query_image=None,
    limit=5,
    selected_documents=None,
    expand_graph=True,
    extra_neighbors=2,
):
    qdrant = QdrantClient(path="./qdrant_data")

    if query_image is not None:
        if isinstance(query_image, Path):
            query_image = Image.open(query_image)
        image_description = describe_query_image(query_image)
        query_text = f"{image_description}\n\nQuestion: {question}"
    else:
        query_text = question

    query_vector = embed_text(query_text)

    query_limit = max(limit * 4, limit + 5)
    results = qdrant.query_points(
        collection_name="vision_rag",
        query=query_vector,
        limit=query_limit,
    )

    points = []
    for point in results.points:
        if selected_documents and point.payload.get("document") not in selected_documents:
            continue
        points.append(
            {
                "point_id": point.id,
                "page_path": point.payload.get("page_path"),
                "document": point.payload.get("document"),
                "pdf_path": point.payload.get("pdf_path"),
                "page_number": point.payload.get("page_number"),
                "description": point.payload.get("description"),
                "score": point.score,
            }
        )
        if len(points) >= limit:
            break

    if expand_graph:
        page_paths = [p["page_path"] for p in points if p.get("page_path")]
        neighbors = get_graph_neighbors(page_paths, max_neighbors=extra_neighbors)
        graph = load_graph()

        for neighbor_path in neighbors:
            if any(n["page_path"] == neighbor_path for n in points):
                continue
            payload = _load_payload_for_path(neighbor_path, graph)
            if payload:
                points.append(payload)
                if len(points) >= limit + extra_neighbors:
                    break

    qdrant.close()
    return points[: min(len(points), limit + extra_neighbors)]


def _load_payload_for_path(page_path, graph):
    if not page_path:
        return None

    node = graph.get("nodes", {}).get(page_path)
    if not node:
        return None

    return {
        "point_id": None,
        "page_path": page_path,
        "document": node.get("document"),
        "pdf_path": None,
        "page_number": node.get("page_number"),
        "description": " | ".join(node.get("concepts", [])) or Path(page_path).name,
        "score": None,
    }
