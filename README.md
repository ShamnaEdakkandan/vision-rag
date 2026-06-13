# Vision RAG — Gemini Vision Edition

A visual document intelligence system that reads PDFs the way a human does — page by page, visually. Ask questions in plain English and get answers grounded in what the document actually shows.

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

### Level 2 — Agentic Search (LangGraph)

Instead of a single retrieval pass, a LangGraph agent decides whether the retrieved pages are enough to fully answer the question. If not, it searches again and combines results.

```
Question → Search → Enough information?
                         │
                        No → Search Again → Combine → Answer
                         │
                        Yes → Answer
```

This improves accuracy on questions that span multiple pages.

### Level 3 — GraphRAG (NetworkX)

After ingestion, Gemini extracts key concepts from each page. NetworkX builds a knowledge graph linking pages that share related concepts.

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
| pdf2image | Convert PDF pages to images |
| Pillow | Image processing and cleanup |
| Gemini 2.5 Flash | Vision understanding and answer generation |
| text-embedding-004 | Generate embeddings for page descriptions and queries |
| NumPy | Store and load vectors as .npy files |
| python-dotenv | Load GEMINI_API_KEY from .env |
| LangGraph | Agentic search workflow |
| NetworkX | Knowledge graph for GraphRAG |
| Streamlit | Web UI |
| Qdrant | Vector database (optional upgrade from .npy) |

---

## Project Structure

```
vision-rag/
├── .env                  ← GEMINI_API_KEY=your_key_here
├── pdfs/                 ← drop PDF files here
├── pages/                ← converted page images
├── index/
│   ├── vectors.npy       ← stored page embeddings
│   └── metadata.json     ← page number to file mapping
├── graph/
│   └── graph.json        ← NetworkX knowledge graph
├── rag.py                ← shared Gemini client and embedding setup
├── ingest.py             ← PDF to index pipeline
├── query.py              ← search and answer pipeline
├── agent.py              ← LangGraph agentic search
├── graph_builder.py      ← builds GraphRAG knowledge graph
├── multimodal.py         ← image query handling
├── app.py                ← Streamlit web UI
└── requirements.txt
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