from pathlib import Path
import json

import fitz
from PIL import Image

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from rag import client


# -----------------------------
# CONFIG
# -----------------------------

COLLECTION_NAME = "vision_rag"

# qdrant = QdrantClient(
#     path="./qdrant_data"
# )


# -----------------------------
# INGEST PDF
# -----------------------------

def ingest_pdf(pdf_path):

    qdrant = QdrantClient(
    path="./qdrant_data"
)

    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        raise FileNotFoundError(pdf_path)

    document_name = pdf_file.stem

    print(f"\nProcessing: {document_name}")

    # -----------------------------
    # OUTPUT FOLDER
    # -----------------------------

    pages_dir = Path("pages") / document_name

    pages_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    descriptions = {}

    # -----------------------------
    # PDF -> IMAGES
    # -----------------------------

    pdf = fitz.open(pdf_path)

    for page_number in range(len(pdf)):

        page = pdf.load_page(page_number)

        pix = page.get_pixmap(
            matrix=fitz.Matrix(2, 2)
        )

        image_path = (
            pages_dir /
            f"page_{page_number + 1}.png"
        )

        pix.save(str(image_path))

        print(
            f"Saved: {image_path}"
        )

    pdf.close()

    # -----------------------------
    # DESCRIBE PAGES
    # -----------------------------

    image_files = sorted(
        pages_dir.glob("*.png")
    )

    for image_path in image_files:

        print(
            f"Describing: {image_path.name}"
        )

        image = Image.open(image_path)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                image,
                """
                Describe this document page.

                Include:

                - title
                - headings
                - main topics
                - tables
                - charts
                - diagrams
                - important information

                Keep the description detailed
                and searchable.
                """
            ]
        )

        descriptions[
            str(image_path)
        ] = response.text

    # -----------------------------
    # SAVE DESCRIPTIONS
    # -----------------------------

    index_dir = Path("index")

    index_dir.mkdir(
        exist_ok=True
    )

    description_file = (
        index_dir /
        f"{document_name}_descriptions.json"
    )

    with open(
        description_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            descriptions,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("\nDescriptions saved.")

    # -----------------------------
    # EMBEDDINGS
    # -----------------------------

    points = []

    for page_id, (
        page_path,
        description
    ) in enumerate(
        descriptions.items()
    ):

        print(
            f"Embedding: {page_path}"
        )

        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=description
        )

        vector = (
            response
            .embeddings[0]
            .values
        )

        points.append(
            PointStruct(
                id=page_id,
                vector=vector,
                payload={
                    "document": document_name,
                    "page_path": page_path,
                    "description": description
                }
            )
        )

    # -----------------------------
    # UPLOAD TO QDRANT
    # -----------------------------

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    print(
        f"\nUploaded {len(points)} pages to Qdrant."
    )

    print("\nDONE")

    qdrant.close()


# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":

    pdf_path = input(
        "PDF Path: "
    ).strip()

    ingest_pdf(pdf_path)