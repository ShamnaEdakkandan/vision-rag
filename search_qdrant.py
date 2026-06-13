from qdrant_client import QdrantClient
from rag import client


def retrieve_pages(
    question,
    limit=3
):

    qdrant = QdrantClient(
        path="./qdrant_data"
    )

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=question
    )

    query_vector = (
        response.embeddings[0].values
    )

    results = qdrant.query_points(
        collection_name="vision_rag",
        query=query_vector,
        limit=limit
    )

    qdrant.close()

    return results.points