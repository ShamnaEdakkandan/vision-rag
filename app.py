import streamlit as st
from pathlib import Path
from PIL import Image

from ingest_pdf import ingest_pdf
from answer_engine import answer_question


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
            st.image(
                page["page_path"],
                caption=format_page_caption(page),
                width=300,
            )
            if page.get("description"):
                st.write(page["description"][:180] + ("..." if len(page["description"]) > 180 else ""))


st.set_page_config(
    page_title="Vision RAG",
    page_icon="📄",
    layout="wide",
)

st.markdown(
    """
    <style>
    .section-title { font-size:1.8rem; font-weight:700; margin-bottom:0.2rem; }
    .section-desc { color:#555555; margin-top:0; margin-bottom:1rem; }
    .stButton>button { width:100%; }
    .metadata-box { background:#f7f7f7; padding:1rem; border-radius:0.75rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("# 📄 Vision RAG")
st.write("A polished Streamlit UI for visual PDF search, multimodal queries, and page-level retrieval.")

if "indexed" not in st.session_state:
    st.session_state.indexed = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "available_docs" not in st.session_state:
    st.session_state.available_docs = get_indexed_documents()
if "last_results" not in st.session_state:
    st.session_state.last_results = []

with st.sidebar:
    st.header("Search settings")
    st.write("Select indexed documents, upload an optional query image, and tune retrieval.")

    selected_documents = st.multiselect(
        "Search documents",
        st.session_state.available_docs,
        default=st.session_state.available_docs,
        help="Limit search to one or more indexed documents.",
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

main_col, side_col = st.columns([3, 1])
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
            st.session_state.available_docs = get_indexed_documents()
            st.success("PDF indexed successfully!")

    st.divider()
    st.subheader("Ask a question")
    with st.form("query_form"):
        question = st.text_input("What do you want to know?")
        search_button = st.form_submit_button("🔍 Search")

    if search_button:
        if not question:
            st.warning("Please enter a question before searching.")
        elif not st.session_state.available_docs:
            st.warning("No indexed documents available. Upload and index a PDF first.")
        else:
            query_image = Image.open(query_image_file) if query_image_file else None
            with st.spinner("Searching for answers..."):
                result = answer_question(
                    question,
                    query_image=query_image,
                    selected_documents=selected_documents or None,
                    limit=max_results,
                    expand_graph=expand_graph,
                )
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
