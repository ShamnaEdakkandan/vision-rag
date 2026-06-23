import streamlit as st
from pathlib import Path
from PIL import Image
import base64

from ingest_pdf import ingest_pdf
from answer_engine import answer_question


def get_base64_of_image(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def get_indexed_documents():
    pages_dir = Path("pages")
    if not pages_dir.exists():
        return []
    return sorted([p.name for p in pages_dir.iterdir() if p.is_dir()])


def format_page_caption(result):
    document = result.get("document") or "unknown"
    page_number = result.get("page_number") or "?"
    score = result.get("score")
    score_text = f"score {round(score, 4)}" if score is not None else "score unavailable"
    return f"{document} · Page {page_number} · {score_text}"


def render_retrieved_pages(page_results):
    if not page_results:
        st.info("No pages retrieved yet.")
        return

    cards = st.columns(min(3, len(page_results)))
    for idx, page in enumerate(page_results):
        card = cards[idx % len(cards)]
        with card:
            st.markdown(f"""
                <div class="result-card">
                    <img src="data:image/png;base64,{get_base64_of_image(page['page_path'])}" style="width:100%; display:block;">
                    <div class="result-metadata">
                        {format_page_caption(page)}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if page.get("description"):
                st.write(page["description"][:120] + ("..." if len(page["description"]) > 120 else ""))


st.set_page_config(
    page_title="Vision RAG",
    page_icon="📄",
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400&display=swap');

    :root {
        --primary: #4f46e5;
        --secondary: #7c3aed;
        --accent: #06b6d4;
        --background: #fcfdfe;
        --card-bg: rgba(255, 255, 255, 0.9);
        --text-main: #0f172a;
        --text-muted: #475569;
        --border-soft: rgba(226, 232, 240, 0.8);
        --aura-indigo: rgba(79, 70, 229, 0.05);
        --aura-violet: rgba(124, 58, 237, 0.05);
    }

    .stApp {
        background-color: var(--background);
        font-family: 'Inter', sans-serif;
    }

    /* Aura Background */
    .aura-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        background: 
            radial-gradient(circle at 15% 15%, var(--aura-indigo) 0%, transparent 40%),
            radial-gradient(circle at 85% 85%, var(--aura-violet) 0%, transparent 40%);
        filter: blur(60px);
    }

    /* Cinematic Header */
    .hero-section {
        padding: 8rem 1rem 6rem 1rem;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
        background: url('https://images.unsplash.com/photo-1639322537228-f710d846310a?q=80&w=2000&auto=format&fit=crop') center/cover no-repeat;
        border-radius: 32px;
        margin: 1rem;
        overflow: hidden;
        border: 1px solid var(--border-soft);
    }

    .hero-section::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(circle at center, rgba(255,255,255,0.7) 0%, rgba(255,255,255,0.95) 100%);
        z-index: 1;
    }

    .hero-tag, .hero-title, .hero-subtitle {
        position: relative;
        z-index: 2;
    }

    .hero-tag {
        display: inline-block;
        padding: 0.3rem 1rem;
        background: white;
        border: 1px solid var(--border-soft);
        border-radius: 100px;
        color: var(--primary);
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 2rem;
    }

    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 6rem;
        font-weight: 900;
        letter-spacing: -0.05em;
        line-height: 0.9;
        color: var(--text-main);
        margin-bottom: 1.5rem;
        text-shadow: 0 10px 40px rgba(255,255,255,0.8), 0 0 20px rgba(79, 70, 229, 0.1);
    }

    .hero-subtitle {
        font-size: 1.15rem;
        color: var(--text-main);
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
        text-align: center;
        opacity: 0.7;
    }

    /* Bento Grid Layout */
    .bento-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
        margin: 1rem auto 4rem auto;
        padding: 0 1rem;
        max-width: 1200px;
    }

    /* Main Content Wrapper */
    .content-wrapper {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 2rem;
    }

    .bento-card {
        background: var(--card-bg);
        border: 1px solid var(--border-soft);
        border-radius: 20px;
        padding: 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 180px;
        position: relative;
        overflow: hidden;
    }

    .card-accent {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: var(--primary);
    }

    .bento-card:hover {
        transform: translateY(-5px);
        border-color: var(--primary);
        box-shadow: 0 10px 25px -10px rgba(0, 0, 0, 0.1);
    }

    .bento-card h3 {
        font-family: 'Outfit', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: var(--text-main);
    }

    .bento-card p {
        font-size: 0.85rem;
        color: var(--text-muted);
        line-height: 1.5;
    }

    /* Custom Command Search */
    .stTextInput input {
        background: white !important;
        border: 1px solid var(--border-soft) !important;
        border-radius: 12px !important;
        padding: 0.8rem 1.2rem !important;
        font-size: 1rem !important;
        font-family: 'Inter', sans-serif !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02) !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1) !important;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 100px !important;
        background: var(--text-main) !important;
        color: white !important;
        padding: 0.8rem 2.5rem !important;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }

    .stButton>button:hover {
        background: var(--primary) !important;
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3) !important;
    }

    /* Result Cards */
    .result-card {
        background: white;
        border: 1px solid var(--border-soft);
        border-radius: 20px;
        overflow: hidden;
        margin-bottom: 2rem;
        transition: transform 0.3s ease;
    }

    .result-card:hover {
        transform: scale(1.03);
    }

    .result-metadata {
        padding: 1rem;
        background: #f8fafc;
        border-top: 1px solid var(--border-soft);
        font-size: 0.8rem;
        color: var(--text-muted);
        font-family: 'JetBrains Mono', monospace;
    }
    </style>

    <div class="aura-bg"></div>

    <div class="hero-section">
        # <div class="hero-tag">System Version 2.0</div>
        <h1 class="hero-title">DocLens</h1>
        <p class="hero-subtitle">Visual-first document intelligence. Connect your complex PDFs to a multimodal retrieval engine that understands exactly what it sees.</p>
    </div>

    <div class="bento-container">
        <div class="bento-card">
            <div class="card-accent" style="background: var(--primary);"></div>
            <h3>Visual-First</h3>
            <p>Engineered for charts, explains diagrams, and processes tables with high precision.</p>
        </div>
        <div class="bento-card">
            <div class="card-accent" style="background: var(--secondary);"></div>
            <h3>Graph Concept RAG</h3>
            <p>Cross-referencing your entire library using high-recall neighbor expansion.</p>
        </div>
        <div class="bento-card">
            <div class="card-accent" style="background: var(--accent);"></div>
            <h3>Zero Hallucination</h3>
            <p>Every answer is tethered directly to original page-level thumbnails.</p>
        </div>
    </div>

    <div class="content-wrapper">
    <!-- Streamlit content will be injected below -->
    """,
    unsafe_allow_html=True,
)

if "indexed" not in st.session_state:
    st.session_state.indexed = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "available_docs" not in st.session_state:
    st.session_state.available_docs = get_indexed_documents()
if "last_results" not in st.session_state:
    st.session_state.last_results = []
if "last_indexed_doc" not in st.session_state:
    st.session_state.last_indexed_doc = None

with st.sidebar:
    st.header("Search settings")
    st.write("Select indexed documents, upload an optional query image, and tune retrieval.")

    default_selection = st.session_state.available_docs
    if st.session_state.last_indexed_doc and st.session_state.last_indexed_doc in st.session_state.available_docs:
        default_selection = [st.session_state.last_indexed_doc]

    selected_documents = st.multiselect(
        "Search scope",
        st.session_state.available_docs,
        default=default_selection,
        help="Select which documents to search through.",
    )
    query_image_file = st.file_uploader(
        "Upload query image",
        type=["png", "jpg", "jpeg"],
        help="Optional image query for charts, diagrams, or screenshots.",
    )
    if query_image_file:
        st.image(Image.open(query_image_file), caption="Query image preview", width=240)

    max_results = st.slider("Max retrieved pages", 1, 6, 3)
    expand_graph = st.checkbox("GraphRAG expansion", value=True)
    st.markdown("---")
    st.write("Built with Gemini Vision, Qdrant, and Streamlit.")

st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)

main_col, side_col = st.columns([2, 1], gap="large")
with main_col:
    st.subheader("Upload and index PDF")
    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        help="Upload a PDF to index its pages into Qdrant.",
    )
    if uploaded_file:
        upload_dir = Path("documents")
        upload_dir.mkdir(exist_ok=True)
        pdf_path = upload_dir / uploaded_file.name
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded: {uploaded_file.name}")
        st.info(f"Saved to: {pdf_path}")

        if st.button("📥 Index PDF"):
            with st.spinner("Indexing PDF..."):
                ingest_pdf(str(pdf_path))
            st.session_state.indexed = True
            st.session_state.last_indexed_doc = uploaded_file.name
            st.session_state.available_docs = get_indexed_documents()
            st.success(f"Successfully indexed {uploaded_file.name}!")
            st.rerun()

    st.subheader("Ask a question")
    with st.form("query_form", border=False):
        question = st.text_input("Search through your documents...", placeholder="e.g. What is the revenue growth?")
        search_button = st.form_submit_button("🔍 Search")

    if search_button:
        if not question:
            st.warning("Please enter a question before searching.")
        elif not st.session_state.available_docs:
            st.warning("No indexed documents available. Upload and index a PDF first.")
        else:
            query_image = Image.open(query_image_file) if query_image_file else None
            with st.spinner("Searching for answers..."):
                try:
                    result = answer_question(
                        question,
                        query_image=query_image,
                        selected_documents=selected_documents or None,
                        limit=max_results,
                        expand_graph=expand_graph,
                    )
                except Exception:
                    result = {
                        "answer": (
                            "Sorry, the answer service is temporarily unavailable. "
                            "Please try again in a few moments."
                        ),
                        "results": [],
                    }
            st.session_state.last_results = result["results"]
            st.session_state.chat_history.append(
                {
                    "question": question,
                    "answer": result["answer"],
                    "results": result["results"],
                }
            )

    answer_tab, history_tab = st.tabs(["Answer", "Chat History"])

    with answer_tab:
        if st.session_state.last_results:
            st.markdown("### Answer")
            st.write(st.session_state.chat_history[-1]["answer"])
            st.markdown("### Retrieved Pages")
            render_retrieved_pages(st.session_state.last_results)
        else:
            st.info("Run a search to see an answer and retrieved page thumbnails.")

    with history_tab:
        if not st.session_state.chat_history:
            st.info("No chat history yet. Ask a question to start.")
        else:
            for item in reversed(st.session_state.chat_history):
                st.markdown(f"**Q:** {item['question']}")
                st.markdown(f"**A:** {item['answer']}")
                with st.expander("Show retrieved pages"):
                    render_retrieved_pages(item["results"])
                st.markdown("---")

with side_col:
    st.markdown("## Quick status")
    st.write(f"**Indexed docs:** {len(st.session_state.available_docs)}")
    if st.session_state.available_docs:
        st.write(
            "**Documents:** " + ", ".join(st.session_state.available_docs)
        )
    st.write(f"**Last query:** {st.session_state.chat_history[-1]['question'] if st.session_state.chat_history else 'None'}")
    if st.button("🧹 Clear history"):
        st.session_state.chat_history = []
        st.success("Chat history cleared.")

st.markdown("</div>", unsafe_allow_html=True)
