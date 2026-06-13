from pathlib import Path
import json
import numpy as np

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct


# Connect

client = QdrantClient(
    path="./qdrant_data"
)

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

with open(
    "index/page_descriptions.json",
    "r",
    encoding="utf-8"
) as f:
    descriptions = json.load(f)

# Build points

points = []

for idx, page_path in enumerate(page_paths):

    points.append(
        PointStruct(
            id=idx,
            vector=embeddings[idx].tolist(),
            payload={
                "page_path": page_path,
                "description": descriptions[page_path]
            }
        )
    )

# Upload

client.upsert(
    collection_name="vision_rag",
    points=points
)

print(
    f"Uploaded {len(points)} vectors."
)

client.close()