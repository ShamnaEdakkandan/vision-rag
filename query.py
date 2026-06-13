from pathlib import Path
import json
from PIL import Image

from rag import client

PAGES_DIR = Path("pages")
INDEX_DIR = Path("index")

INDEX_DIR.mkdir(exist_ok=True)

page_descriptions = {}

for image_path in PAGES_DIR.rglob("*.png"):

    print(f"Analyzing {image_path.name}...")

    image = Image.open(image_path)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            image,
            """
            Describe this document page.

            Include:
            - title
            - main topics
            - tables
            - charts
            - important information

            Keep the description searchable.
            """
        ]
    )

    page_descriptions[str(image_path)] = response.text

    print(response.text[:200])

with open(
    INDEX_DIR / "page_descriptions.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        page_descriptions,
        f,
        indent=2,
        ensure_ascii=False
    )

print("Index saved.")