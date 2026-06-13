import json
from PIL import Image

from qdrant_client import QdrantClient
from rag import client


# -----------------------------
# Connect Qdrant
# -----------------------------

qdrant = QdrantClient(
    path="./qdrant_data"
)

# -----------------------------
# User Question
# -----------------------------

question = input("Question: ")

# -----------------------------
# Embed Question
# -----------------------------

response = client.models.embed_content(
    model="gemini-embedding-001",
    contents=question
)

query_vector = response.embeddings[0].values

# -----------------------------
# Search Qdrant
# -----------------------------

results = qdrant.query_points(
    collection_name="vision_rag",
    query=query_vector,
    limit=5
)

# -----------------------------
# Debug Retrieval
# -----------------------------

print("\nTop Matches:\n")

for point in results.points:

    print(
        point.payload["page_path"]
    )

    print(
        "Score:",
        round(point.score, 4)
    )

    print()

# -----------------------------
# Load Images
# -----------------------------

# -----------------------------
# Load Images + Metadata
# -----------------------------

images = []
page_info = []

for point in results.points:

    page_path = point.payload["page_path"]

    score = point.score

    description = point.payload["description"]

    image = Image.open(page_path)

    images.append(image)

    page_info.append(
        f"""
Document: {point.payload['document']}
Page: {page_path}
Score: {round(score,4)}

Description:
{description}
"""
    )

# -----------------------------
# Prompt
# -----------------------------

prompt = f"""
You are a Vision RAG assistant.

Question:
{question}

Retrieved Context:
{chr(10).join(page_info)}

Instructions:

1. Carefully inspect ALL retrieved page images.
2. Use both:
   - the page images
   - the retrieved descriptions

3. Answer only from the retrieved pages.

4. If information exists across multiple pages,
   combine the information.

5. Mention which page(s) were used.

6. If charts, tables, diagrams,
   or images contain the answer,
   use them.

7. If the answer is missing,
   reply exactly:

Answer not found in retrieved pages.

8. Do not hallucinate.
"""

# -----------------------------
# Ask Gemini
# -----------------------------

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=images + [prompt]
)

# -----------------------------
# Output
# -----------------------------

print("=" * 60)

print("\nAnswer:\n")

print(response.text)

# -----------------------------
# Close Qdrant
# -----------------------------

qdrant.close()