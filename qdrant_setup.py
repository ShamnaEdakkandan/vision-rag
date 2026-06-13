from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams
from qdrant_client.models import Distance

client = QdrantClient(
    path="./qdrant_data"
)

client.create_collection(
    collection_name="vision_rag",
    vectors_config=VectorParams(
        size=3072,
        distance=Distance.COSINE
    )
)

print("Collection created.")
client.close()