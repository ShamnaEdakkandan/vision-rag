from PIL import Image

from rag import client
from search_qdrant import retrieve_pages


def answer_question(question):

    results = retrieve_pages(
        question,
        limit=3
    )

    images = []
    page_info = []

    for point in results:

        page_path = point.payload["page_path"]

        description = point.payload["description"]

        image = Image.open(page_path)

        images.append(image)

        page_info.append(
            f"""
Document: {point.payload['document']}
Page: {page_path}
Score: {round(point.score,4)}

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

4. Use charts, tables, diagrams,
   and images if relevant.

5. If answer not found:

Answer not found in retrieved pages.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=images + [prompt]
    )

    return response.text