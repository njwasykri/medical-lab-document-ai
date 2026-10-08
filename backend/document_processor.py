import fitz
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    lang="en",
    enable_mkldnn=False
)


def extract_text_from_pdf(pdf_path):
    document = fitz.open(pdf_path)

    all_pages = []

    for page_number, page in enumerate(document, start=1):

        page_text = page.get_text()

        # Normal PDF with selectable text
        if page_text.strip():

            all_pages.append({
                "page": page_number,
                "source": "pdf_text",
                "text": page_text
            })

        # Scanned/image PDF
        else:

            pix = page.get_pixmap(dpi=200)
            print(f"Running PaddleOCR on page {page_number}")

            image_path = f"backend/uploads/temp_page_{page_number}.png"
            pix.save(image_path)

            result = ocr.predict(image_path)

            if result:
                texts = result[0]["rec_texts"]
                scores = result[0]["rec_scores"]
                
                print("OCR CONFIDENCE SCORES:", scores)

                # Get OCR coordinates if available
                boxes = result[0].get("rec_boxes", [])

                page_items = []

                for i, text in enumerate(texts):

                    if i < len(boxes):
                        box = boxes[i]

                        page_items.append({
                            "text": text,
                            "box": box.tolist()
                        })

                    else:
                        page_items.append({
                            "text": text,
                            "box": None
                        })

                all_pages.append({
                    "page": page_number,
                    "source": "ocr",
                    "items": page_items
                })

    document.close()

    return all_pages