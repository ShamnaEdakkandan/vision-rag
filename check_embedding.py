from rag import client

response = client.models.embed_content(
    model="gemini-embedding-001",
    contents="hello world"
)

print(
    len(
        response.embeddings[0].values
    )
)