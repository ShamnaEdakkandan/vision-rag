from PIL import Image

from rag import client
from search_qdrant import retrieve_pages


def answer_question(
    question,
    query_image=None,
    selected_documents=None,
    limit=3,
    expand_graph=True,
):
    results = retrieve_pages(
        question,
        query_image=query_image,
        limit=limit,
        selected_documents=selected_documents,
        expand_graph=expand_graph,
        extra_neighbors=2,
    )

    images = []
    page_info = []

    if query_image is not None:
        images.append(query_image)

    for result in results:
        page_path = result["page_path"]
        description = result.get("description", "")
        image = Image.open(page_path)
        images.append(image)

        page_info.append(
            f"""
Document: {result.get('document', 'unknown')}
Page: {page_path}
Score: {round(result.get('score') or 0, 4)}

Description:
{description}
"""
        )

    prompt = f"""
You are a Vision RAG assistant.

Question:
{question}

Retrieved Context:
{chr(10).join(page_info)}

Instructions:

1. Use BOTH:
   - page images
   - page descriptions

2. Answer only from retrieved pages.

3. Mention which page(s) were used.

4. Use charts, tables, diagrams, and images if relevant.

5. If the answer is missing from retrieved pages, reply exactly:
Answer not found in retrieved pages.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=images + [prompt]
    )

    return {
        "answer": response.text,
        "results": results,
    }
