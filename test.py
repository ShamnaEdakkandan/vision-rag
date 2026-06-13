from rag import client

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="hello"
)

print(response.text)