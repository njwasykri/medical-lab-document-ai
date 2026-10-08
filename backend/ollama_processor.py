import ollama
import base64


def ask_qwen(image_paths, text):

    limited_text = text[:10000]

    # Make sure image_paths is always a list
    if isinstance(image_paths, str):
        image_paths = [image_paths]

    # Convert images to base64
    encoded_images = []

    for image_path in image_paths:

        with open(image_path, "rb") as image_file:
            image_base64 = base64.b64encode(
                image_file.read()
            ).decode("utf-8")

        encoded_images.append(image_base64)

    response = ollama.chat(
        model="qwen2.5vl:3b",

        options={
            "num_ctx": 8192
        },

        messages=[
            {
                "role": "user",

                "content": f"""
You are a document data extraction assistant.

You are given multiple images representing different pages of ONE document.

Analyze ALL pages carefully before producing the final answer.

IMPORTANT RULES:

1. Inspect EVERY page of the document.
2. Do NOT stop after finding the first section.
3. Extract information from ALL sections.
4. The document images are the MAIN source.
5. OCR text is supporting information only.
6. If OCR text and the image disagree, trust the image.
7. Do NOT guess or invent information.
8. Keep numbers exactly as shown in the document.
9. Do not omit clearly visible test results.
10. Keep each test matched with its correct result.
11. Keep each result matched with its correct unit.
12. Keep each result matched with its correct reference range.
13. Keep interpretations such as Reactive, Non-Reactive, Positive, Negative, etc.
14. If a value is not available, write "Not clearly detected".
15. Do not combine information from different rows.
16. Include ALL laboratory sections, including Haematology, Biochemistry, Immunology, Serology, Endocrinology and other sections if present.
17. The Flag column is NOT the Reference Range. Never use H, L, High, Low, Abnormal, or similar flag values as the Reference Range.
18. If a flag appears between Result and Reference Range, ignore the flag for the final output. Find the actual reference range from the same test row.

IMPORTANT FOR LABORATORY REPORTS:

Every visible test row must be considered individually.

For example, if the document contains:

HBSAb (antibody)
Result: 35.7
Unit: miU/mL
Reference Range: 10.0 - 100.0 miU/mL

then extract it as one complete test result.

If a test has an interpretation instead of a numerical result, include the interpretation.

If a section contains several tests, extract ALL of them.

OUTPUT FORMAT:

| Parameter | Result | Unit | Reference Range |
|---|---|---|---|

IMPORTANT:

Return ONLY the laboratory results table.

Do not include:
- Document Information
- Section
- Interpretation column
- Other Information
- Explanations
- Summary
- Additional comments

Every visible laboratory test must be included as a separate row.

Keep the exact parameter name as shown in the document.

If the test has a numerical result, put the numerical value in the Result column.

If the test result is a word or interpretation such as Reactive, Non-Reactive, Positive, Negative, Detected, Not Detected, or similar, put that word in the Result column.

Do not create a separate interpretation column.

If a value is not clearly visible, write "Not clearly detected".

Keep the correct unit with each result.

Keep the correct reference range with each result.

Do not combine different tests into one row.

Do not omit any visible laboratory test.

Before answering, check EVERY page and EVERY laboratory section again to make sure ALL visible laboratory tests are included.

OCR TEXT FROM THE DOCUMENT:

{limited_text}
""",

                "images": encoded_images
            }
        ]
    )

    return response["message"]["content"]

def extract_missed_information_with_vlm(image_paths, ocr_text):

    prompt = f"""
You are a document extraction assistant.

Compare the document images with the OCR text.

Your task is to identify information that was:
- missed by OCR
- incompletely extracted by OCR
- incorrectly extracted by OCR

Pay special attention to:
- Laboratory test parameters
- Results
- Units
- Reference ranges
- Reactive / Non-Reactive
- Positive / Negative
- Detected / Not Detected
- H / L / High / Low flags
- Complex table layouts

The Flag column is NOT the Reference Range.

Only return information that OCR missed, failed to extract completely,
or incorrectly interpreted.

Do not return information that OCR extracted correctly.

OUTPUT FORMAT:

| Parameter | Result | Unit | Reference Range |
|---|---|---|---|

If no additional information is found, return:

No additional information detected.

CRITICAL REFERENCE RANGE RULE:

The output MUST contain exactly 4 columns:

| Parameter | Result | Unit | Reference Range |

Never create a fifth column.

Flags such as:
- H
- L
- High
- Low
- Abnormal

are NOT reference ranges.

If a flag appears in the document, completely ignore it when constructing the Reference Range column.

For example, if the document shows:

TRIGLYCERIDES    0.53    Low    mmol/L    1.00 - 2.30

the output MUST be:

| TRIGLYCERIDES | 0.53 | mmol/L | 1.00 - 2.30 |

NOT:

| TRIGLYCERIDES | 0.53 | mmol/L | Low | 1.00 - 2.30 |

If the document shows:

CHOLESTEROL    6.91    High    mmol/L    1.00 - 5.20

the output MUST be:

| CHOLESTEROL | 6.91 | mmol/L | 1.00 - 5.20 |

The words High and Low must NEVER appear inside the Reference Range column.

The Reference Range column must contain ONLY the actual reference range shown in the document, such as:
- 135 - 145
- 3.90 - 6.00
- 1.00 - 5.20
- 0.10 - 3.90

If the actual reference range cannot be clearly identified from the image, write:

Not clearly detected

Do not guess the reference range.

OCR TEXT:

{ocr_text}
"""

    if isinstance(image_paths, str):
        image_paths = [image_paths]

    encoded_images = []

    for image_path in image_paths:

        with open(image_path, "rb") as image_file:
            image_base64 = base64.b64encode(
                image_file.read()
            ).decode("utf-8")

        encoded_images.append(image_base64)

    response = ollama.chat(
        model="qwen2.5vl:3b",

        options={
            "num_ctx": 8192
        },

        messages=[
            {
                "role": "user",
                "content": prompt,
                "images": encoded_images
            }
        ]
    )

    return response["message"]["content"]