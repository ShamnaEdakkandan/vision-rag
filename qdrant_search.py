import numpy as np

from qdrant_client import QdrantClient

from rag import client


# Connect Qdrant

qdrant = QdrantClient(
    path="./qdrant_data"
)

# Question

question = input("Question: ")

# Embed question

response = client.models.embed_content(
    model="gemini-embedding-001",
    contents=question
)

query_vector = response.embeddings[0].values

# Search

results = qdrant.query_points(
    collection_name="vision_rag",
    query=query_vector,
    limit=3
)

print("\nResults:\n")

for point in results.points:

    print(
        point.payload["page_path"]
    )

    print(
        "Score:",
        round(point.score, 4)
    )

    print()

qdrant.close()