# Vision RAG — Overview

## What this project is

This repo is a visual RAG system for PDF documents. It does not treat PDFs as plain text first. Instead, it converts each PDF page into an image and uses Gemini Vision to understand the page visually. That means it can handle:

- charts and graphs
- tables and merged cells
- diagrams and visuals
- scanned or image-based pages
- layout-heavy documents
- mixed text + visual content

The system combines:

- visual page understanding
- semantic embeddings
- vector search in Qdrant
- GraphRAG-style neighbor expansion
- a Streamlit UI with thumbnails and chat history

---

## File-by-file description

### `app.py`

This is the Streamlit web UI.

It handles:

- PDF upload and indexing
- question input
- optional query image upload
- document selection for search
- retrieved page thumbnails
- answer display
- chat history
- index status and UI flow

This file is the main user-facing interface and the simplest way to demonstrate the system.

### `ingest_pdf.py`

This is the ingestion pipeline.

It does:

- convert each PDF page to PNG images using `fitz`
- call Gemini Vision to describe each page image
- embed page descriptions with Gemini embedding model
- upload page vectors and metadata into Qdrant
- save page descriptions and metadata to `index/`
- build a GraphRAG graph from page concepts

The output is:

- visual page images in `pages/<document>/`
- page descriptions in `index/<document>_descriptions.json`
- page metadata in `index/<document>_metadata.json`
- a Qdrant collection named `vision_rag`
- a graph file at `index/graph.json`

### `search_qdrant.py`

This is the retrieval module.

It does:

- embed the user question
- optionally describe a query image and combine it with text
- query Qdrant to find semantically closest page vectors
- optionally restrict to selected documents
- optionally expand retrieval using GraphRAG neighbors

It returns a list of retrieved page results with metadata.

### `answer_engine.py`

This is the answer generation module.

It does:

- call `search_qdrant.retrieve_pages(...)`
- load each retrieved page image
- build a grounded prompt containing question, retrieved context, and page descriptions
- send images + prompt to Gemini Vision
- return the final answer and retrieval results

The answer is produced from the retrieved pages, not from the model alone.

### `rag.py`

This is the shared Gemini client setup.

It:

- reads `GEMINI_API_KEY` from `.env`
- creates `client = genai.Client(api_key=API_KEY)`
- exposes `client` for every other module

### `graph_builder.py`

This is the GraphRAG helper module.

It:

- extracts key concepts from page descriptions
- builds a page graph connecting pages with overlapping concepts
- saves the graph to `index/graph.json`
- supports neighbor expansion during retrieval

The graph is lightweight and helps broaden retrieval when relevant pages are conceptually connected.

---

## Working flow

### 1. Upload and index

1. User uploads a PDF through `app.py`.
2. The file is saved to `documents/`.
3. The user clicks `Index PDF`.
4. `ingest_pdf.py` converts the PDF pages into images.
5. Gemini Vision describes each image.
6. Descriptions are embedded into vectors.
7. Vectors and metadata are stored in Qdrant.
8. Metadata and descriptions are also saved to disk.
9. A GraphRAG graph is built from page concepts.

### 2. Ask a question

1. User enters a question in `app.py`.
2. User may optionally upload a query image.
3. `answer_engine.py` calls `search_qdrant.retrieve_pages(...)`.
4. If there is a query image, it is described by Gemini and combined with the question.
5. The combined query is embedded.
6. Qdrant is searched for the closest page embeddings.
7. The top pages are returned with their metadata.
8. If graph expansion is enabled, related neighbor pages are also included.
9. `answer_engine.py` loads the retrieved page images.
10. It builds a prompt containing:
    - the question
    - page descriptions
    - the retrieved pages
11. Gemini Vision generates the final answer.
12. `app.py` renders the answer, thumbnails, and chat history.

---

## Important concepts

### Visual-first retrieval

Most PDF QA systems rely on OCR or text extraction first. This repo does the opposite:

- convert the page into an image
- use Gemini Vision to understand the entire page visually

That preserves:

- charts and graphs
- table structure
- page layout
- diagrams
- scanned content

### Semantic embeddings

Page descriptions are embedded into vectors, and the question is embedded the same way. Retrieval is done by vector similarity, not by keywords.

### Multimodal query

The system supports both:

- text-only questions
- text + image questions

If the user uploads an image, the image is described and that description becomes part of the query.

### GraphRAG-style expansion

Pages with shared concepts are connected in a graph. When the top matches are retrieved, the system can also bring in neighbor pages that are conceptually related, improving recall.

### Grounded answer generation

The final answer is generated from retrieved page images and descriptions. That keeps the response tied to actual page content.

---

## What to highlight on LinkedIn

If you post about this project, emphasize:

- Visual-first PDF retrieval using Gemini Vision
- Page-level search for charts, tables, diagrams, and scanned pages
- Multimodal queries: text + image
- Semantic search with Qdrant vectors
- Graph-based retrieval expansion
- Streamlit UI with thumbnails and chat history
- Grounded answer generation from retrieved pages

### Short LinkedIn highlights

- Built a visual RAG PDF assistant with Gemini Vision
- Supports PDF pages, charts, and diagrams without OCR-first text extraction
- Added multimodal search with image + question input
- Used Qdrant for semantic page retrieval and GraphRAG expansion
- Built a clean Streamlit experience with retrieved page thumbnails

---

## Sample explanation flow for someone else

1. Start with the problem:
   - "PDF chatbots usually fail on charts, tables, and scanned pages because they only use text extraction."
2. Explain the approach:
   - "This system reads each PDF page as an image and lets Gemini Vision understand the page visually."
3. Describe the pipeline:
   - "We index pages by generating descriptions and embeddings, store them in a vector database, then search and answer questions from retrieved page content."
4. Mention the key features:
   - "It supports multimodal queries, multi-document search, page thumbnails, and chat history."
5. Emphasize the benefit:
   - "That means better answers on visual reports, presentations, and scanned documents."

---

## Recommended structure for a short read

If you want to present this as a single readable page, use these sections:

1. Project summary
2. Why visual retrieval matters
3. Architecture overview
4. File and workflow explanation
5. Feature highlights
6. LinkedIn-ready summary

This `overview.md` is already organized in that way, so you can use it directly as a reference or share it with someone else.
