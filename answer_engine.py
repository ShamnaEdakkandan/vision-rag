from PIL import Image
import google.genai.errors as genai_errors

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

Retrieved Context (Ranked by Relevance):
{chr(10).join(page_info)}

Instructions:

1. Prioritize the most relevant document(s) that directly answer the question: "{question}".
2. Use BOTH image content and descriptions provided in the context.
3. Organize your answer logically: Start with the most direct answer, then provide supporting details from other pages if relevant.
4. Mention specifically which document and page(s) were used for each part of your answer.
5. If the answer is missing from the retrieved pages, reply exactly:
Answer not found in retrieved pages.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=images + [prompt]
        )
        answer_text = response.text
    except genai_errors.ServerError:
        answer_text = (
            "The Gemini model is currently unavailable due to high demand. "
            "Please try again in a few moments."
        )
    except genai_errors.APIError:
        answer_text = (
            "An error occurred while generating the answer. "
            "Please try again later."
        )

    return {
        "answer": answer_text,
        "results": results,
    }
