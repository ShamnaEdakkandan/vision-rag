from pathlib import Path
import json
import numpy as np

from rag import client

INDEX_FILE = Path("index/page_descriptions.json")

with open(
    INDEX_FILE,
    "r",
    encoding="utf-8"
) as f:
    page_descriptions = json.load(f)

embeddings = []
page_paths = []

for page_path, description in page_descriptions.items():

    print(f"Embedding: {page_path}")

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=description
    )

    embeddings.append(response.embeddings[0].values)
    page_paths.append(page_path)

np.save(
    "index/page_embeddings.npy",
    np.array(embeddings)
)

with open(
    "index/page_paths.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(page_paths, f, indent=2)

print("Embeddings saved.")