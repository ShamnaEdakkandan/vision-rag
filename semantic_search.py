from pathlib import Path
import json
import numpy as np

from rag import client

# Load embeddings
embeddings = np.load(
    "index/page_embeddings.npy"
)

with open(
    "index/page_paths.json",
    "r",
    encoding="utf-8"
) as f:
    page_paths = json.load(f)

question = input("Question: ")

# Embed question
response = client.models.embed_content(
    model="gemini-embedding-001",
    contents=question
)

query_vector = np.array(
    response.embeddings[0].values
)

# Cosine similarity
scores = []

for i, page_vector in enumerate(embeddings):

    similarity = np.dot(
        query_vector,
        page_vector
    ) / (
        np.linalg.norm(query_vector)
        * np.linalg.norm(page_vector)
    )

    scores.append(
        (
            page_paths[i],
            similarity
        )
    )

scores.sort(
    key=lambda x: x[1],
    reverse=True
)

print("\nTop Matches:\n")

for page, score in scores[:3]:
    print(page)
    print("Score:", round(score, 4))
    print()