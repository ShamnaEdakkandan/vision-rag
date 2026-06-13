import fitz 
from pathlib import Path

PDF_FOLDER = Path("pdfs")
PAGES_FOLDER = Path("pages")

PAGES_FOLDER.mkdir(exist_ok=True)

pdf_files = list(PDF_FOLDER.glob("*.pdf"))

if not pdf_files:
    print("No PDFs found in /pdfs")
    exit()

for pdf_path in pdf_files:
    print(f"\nProcessing: {pdf_path.name}")

    doc = fitz.open(pdf_path)

    pdf_output_folder = PAGES_FOLDER / pdf_path.stem
    pdf_output_folder.mkdir(exist_ok=True)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)

        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

        image_path = pdf_output_folder / f"page_{page_num+1}.png"

        pix.save(str(image_path))

        print(f"Saved: {image_path}")

    print(f"Finished {pdf_path.name}")