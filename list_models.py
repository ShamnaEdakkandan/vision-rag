from rag import client

for model in client.models.list():
    print(model.name)