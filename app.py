import streamlit as st
from pathlib import Path

from ingest_pdf import ingest_pdf
from answer_engine import answer_question


# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(
    page_title="Vision RAG",
    layout="wide"
)

# -----------------------------
# TITLE
# -----------------------------

st.title("📄 Vision RAG")

st.markdown("""
Upload a PDF and ask questions about:

- Text
- Images
- Charts
- Tables
- Diagrams
""")

# -----------------------------
# SESSION STATE
# -----------------------------

if "indexed" not in st.session_state:
    st.session_state.indexed = False

# -----------------------------
# FILE UPLOAD
# -----------------------------

uploaded_file = st.file_uploader(
    "Upload PDF",
    type=["pdf"]
)

# -----------------------------
# SAVE PDF
# -----------------------------

if uploaded_file:

    st.success(
        f"Uploaded: {uploaded_file.name}"
    )

    st.write(
        f"Size: {round(uploaded_file.size / 1024, 2)} KB"
    )

    upload_dir = Path("documents")

    upload_dir.mkdir(
        exist_ok=True
    )

    pdf_path = (
        upload_dir /
        uploaded_file.name
    )

    with open(
        pdf_path,
        "wb"
    ) as f:

        f.write(
            uploaded_file.getbuffer()
        )

    st.info(
        f"Saved to: {pdf_path}"
    )

    # -----------------------------
    # INDEX BUTTON
    # -----------------------------

    if st.button(
        "📥 Index PDF"
    ):

        with st.spinner(
            "Indexing PDF..."
        ):

            ingest_pdf(
                str(pdf_path)
            )

        st.session_state.indexed = True

        st.success(
            "PDF Indexed Successfully!"
        )

# -----------------------------
# QUESTION SECTION
# -----------------------------

st.divider()

st.subheader(
    "Ask Questions"
)

question = st.text_input(
    "Enter your question"
)

if st.button(
    "🔍 Search"
):

    if not question:

        st.warning(
            "Enter a question first."
        )

    elif not st.session_state.indexed:

        st.warning(
            "Please index a PDF first."
        )

    else:

        with st.spinner(
            "Searching..."
        ):

            answer = answer_question(
                question
            )

        st.subheader(
            "Answer"
        )

        st.write(
            answer
        )