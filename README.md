# Vision RAG — Gemini Vision Edition

A visual document intelligence system that reads PDFs the way a human does — page by page, visually. Ask questions in plain English, upload a query image, and get answers grounded in what the document actually shows.

This repo now supports:
- PDF page thumbnails
- Chat history
- Multi-document search
- Multimodal queries with image + question
- GraphRAG neighbor expansion

---

## Why This Exists

Normal PDF chatbots extract text using OCR and feed it into an LLM. That breaks completely on:

- Charts and graphs
- Tables with merged cells
- Scanned documents
- Visual layouts and diagrams
- Handwritten notes

Instead of extracting text first, this system converts every PDF page into an image and uses Gemini Vision to understand the page visually — text, charts, tables, diagrams, layout, and visual relationships — just like a human reader.

---

## Architecture

### Level 1 — Visual Retrieval

Every PDF page is converted to an image. Gemini Vision generates a description for each page:

```
Page 4:
- Revenue chart Q1–Q4
- Revenue increased from 2.1M to 3.4M
- Product A contributed most growth
```

These descriptions are embedded and stored. When a user asks a question, the query is embedded and matched against stored page descriptions. Top pages are retrieved and sent back to Gemini Vision, which reads them directly and generates the final answer.

### Level 2 — Agentic Search

Instead of a single retrieval pass, the system can expand retrieval when initial pages are not sufficient. If the first pass is not enough, it collects additional related pages and combines them into the final answer.

```
Question → Search → Enough information?
                         │
                        No → Search again → Expand retrieval → Answer
                         │
                        Yes → Answer
```

This improves accuracy on questions that span multiple pages.

### Level 3 — GraphRAG

After ingestion, the system builds a lightweight page relationship graph from page descriptions. Pages that share related concepts become linked, and retrieval can expand along those connections.

```
Page 1: Revenue, Sales, Products
Page 2: Revenue, Marketing
Page 3: Customers, Marketing

Graph:
Revenue ── Marketing
   │
 Sales
```

During retrieval, the graph is traversed from the matched concept outward — collecting all connected pages, not just the single closest match.

### Level 4 — Multi-modal Input

Users can upload a screenshot, image, chart, or diagram as their question. Gemini describes the uploaded image, that description becomes the search query, and relevant document pages are retrieved and answered.

```
Upload: chart.png
Gemini: "Bar chart showing quarterly revenue growth"
→ Search → Relevant pages → Answer
```

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| PyMuPDF (fitz) | Convert PDF pages to images |
| Pillow | Image processing and cleanup |
| Gemini 2.5 Flash | Vision understanding and answer generation |
| text-embedding-004 | Generate embeddings for page descriptions and queries |
| NumPy | Store and load vectors as .npy files |
| python-dotenv | Load GEMINI_API_KEY from .env |
| LangGraph | Agentic search workflow |
| JSON / custom graph | Knowledge graph for GraphRAG |
| Streamlit | Web UI |
| Qdrant | Vector database (optional upgrade from .npy) |

---

## Project Structure

```
vision-rag/
├── .env                  ← GEMINI_API_KEY=your_key_here
├── pdfs/                 ← drop PDF files here
├── pages/                ← converted page images organized per PDF
├── index/                ← stored metadata and graph files
│   ├── <document>_descriptions.json
│   ├── <document>_metadata.json
│   └── graph.json        ← GraphRAG neighbor graph
├── rag.py                ← shared Gemini client setup
├── ingest_pdf.py         ← PDF ingestion, page description, embeddings, Qdrant upload
├── search_qdrant.py      ← semantic retrieval with optional image query and GraphRAG expansion
├── answer_engine.py      ← Gemini answer generation over retrieved pages
├── graph_builder.py      ← builds the page relationship graph for GraphRAG
├── app.py                ← Streamlit web UI with thumbnails and chat history
└── test.py               ← example or debug scripts
```

---

## Data Flow

### Ingestion

```
PDF
 ↓
pdf2image → Page Images
 ↓
Gemini Vision → Page Descriptions
 ↓
text-embedding-004 → Vectors
 ↓
vectors.npy + metadata.json
```

### Query

```
Question
 ↓
text-embedding-004 → Query Vector
 ↓
Similarity Search → Relevant Pages
 ↓
Gemini Vision → Answer
```

---

## Setup

### Requirements

- Python 3.12
- Windows / Linux / Mac
- No GPU required

### Install

```bash
mkdir vision-rag && cd vision-rag
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Linux / Mac
source venv/bin/activate

pip install -r requirements.txt
```

### Environment

Create a `.env` file:

```
GEMINI_API_KEY=your_key_here
```

Get a free key at [Google AI Studio](https://aistudio.google.com).

---

## Usage

### Ingest a PDF

```bash
python ingest.py pdfs/report.pdf
```

### Ask a question

```bash
python query.py "What drove revenue growth in Q3?"
```

You can also upload an image alongside your question in the Streamlit UI for multimodal search.

### Launch the UI

```bash
streamlit run app.py
```

---

## Storage

Page vectors are saved as `.npy` files — no database needed. Simple, offline, works for up to a few hundred pages. To scale, swap in Qdrant. Everything else stays the same.

---

## Cost

Gemini 2.5 Flash and text-embedding-004 both have free tiers sufficient for building, running, and demoing this project. No payment required.