from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from backend.document_processor import extract_text_from_pdf
from backend.ollama_processor import ask_qwen, extract_missed_information_with_vlm
import os
import shutil
import fitz

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "backend/uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def home():
    return {"message": "Document AI Backend is Running!"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text and OCR information
    extracted_data = extract_text_from_pdf(file_path)

    # Prepare OCR text for Qwen
    ocr_text = ""

    for page in extracted_data:

        if page["source"] == "pdf_text":
            ocr_text += page["text"] + "\n"

        elif page["source"] == "ocr":

            for item in page["items"]:
                ocr_text += item["text"] + "\n"

    # Convert first PDF page into an image
    document = fitz.open(file_path)

    page = document[0]

    pix = page.get_pixmap(dpi=150)

    image_path = os.path.join(
        UPLOAD_FOLDER,
        "qwen_page.png"
    )

    pix.save(image_path)

    document.close()

    # Send image + OCR text to Qwen
    qwen_result = ask_qwen(
        image_path,
        ocr_text
    )

    vlm_missed_result = extract_missed_information_with_vlm(
    [image_path],
    ocr_text
)
    

    return {
        "filename": file.filename,
        "ocr_text": ocr_text,
        "qwen_result": qwen_result,
        "vlm_missed_result": vlm_missed_result
    }