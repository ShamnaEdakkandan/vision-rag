import json
import numpy as np
from PIL import Image

from rag import client

# -----------------------------
# Load page embeddings
# -----------------------------

embeddings = np.load(
    "index/page_embeddings.npy"
)

with open(
    "index/page_paths.json",
    "r",
    encoding="utf-8"
) as f:
    page_paths = json.load(f)

# -----------------------------
# User question
# -----------------------------

question = input("Question: ")

# -----------------------------
# Embed question
# -----------------------------

response = client.models.embed_content(
    model="gemini-embedding-001",
    contents=question
)

query_vector = np.array(
    response.embeddings[0].values
)

# -----------------------------
# Similarity search
# -----------------------------

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

# Highest score first
scores.sort(
    key=lambda x: x[1],
    reverse=True
)

# Top K pages
top_pages = scores[:2]
print("\nTOP PAGES:")
for page, score in top_pages:
    print(page, score)
    print("\nALL SCORES:")

for page, score in scores:
    print(page, round(score, 4))

# -----------------------------
# Load images
# -----------------------------

images = []
page_info = []

for page_path, score in top_pages:

    image = Image.open(page_path)

    images.append(image)

    page_info.append(
        f"{page_path} (score={round(score, 4)})"
    )

# -----------------------------
# Prompt
# -----------------------------

prompt = f"""
You are answering based only on the retrieved document pages.

Question:
{question}

Retrieved Pages:
{chr(10).join(page_info)}

Instructions:

1. Answer the question clearly.
2. Mention which retrieved page(s) were used.
3. Quote the exact supporting information when possible.
4. If the answer is not present, say:
   "Answer not found in retrieved pages."
5. Do not make up information.
6. Base the answer only on the provided pages.
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

print("\nTop Matches:\n")

for page, score in top_pages:

    print(page)
    print("Score:", round(score, 4))
    print()

print("=" * 50)

print("\nAnswer:\n")

print(response.text)