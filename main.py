import os
import json
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
import pdfplumber
import io
from dotenv import load_dotenv
from prompts import analyze_prompt, compare_prompt, SYSTEM_PROMPT
from utils import generate_pdf_report

load_dotenv()

app = FastAPI(title="AI Recruitment Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


async def read_upload(file, text: str) -> str:
    if file and file.filename:
        file_bytes = await file.read()
        if file.filename.endswith(".pdf"):
            return extract_text_from_pdf(file_bytes)
        return file_bytes.decode("utf-8", errors="ignore")
    return text


def call_groq(prompt: str) -> dict:
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=2000,
        )

        raw = completion.choices[0].message.content
        raw = raw.replace("```json", "").replace("```", "").strip()

        print("\n===== RAW AI RESPONSE =====")
        print(raw[:1000])
        print("===========================\n")

        return json.loads(raw)

    except Exception as e:
        print("GROQ ERROR:", str(e))
        return {
            "error": "AI processing failed: " + str(e)
        }

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/analyze")
async def analyze_candidate(
    cv_text: str = Form(default=""),
    jd_text: str = Form(default=""),
    cv_file: UploadFile = File(default=None),
):
    cv = await read_upload(cv_file, cv_text)
    if not cv:
        return {"error": "Please provide a CV"}
    if not jd_text:
        return {"error": "Please provide a job description"}
    return call_groq(analyze_prompt(cv, jd_text))


@app.post("/compare")
async def compare_candidates(
    cv1_text: str = Form(default=""),
    cv2_text: str = Form(default=""),
    jd_text: str = Form(default=""),
    cv1_file: UploadFile = File(default=None),
    cv2_file: UploadFile = File(default=None),
):
    cv1 = await read_upload(cv1_file, cv1_text)
    cv2 = await read_upload(cv2_file, cv2_text)
    print("CV1:", cv1[:500])
    print("CV2:", cv2[:500])
    if not cv1 or len(cv1.strip()) < 50:
        return {"error": "Candidate 1 CV could not be read. Paste text manually or use another PDF."}
    if not cv2 or len(cv2.strip()) < 50:
        return {"error": "Candidate 2 CV could not be read. Paste text manually or use another PDF."}
    if not jd_text:
        return {"error": "Please provide a job description"}

    result = call_groq(compare_prompt(cv1, cv2, jd_text))
    print("\n===== COMPARE RESULT =====")
    print(json.dumps(result, indent=2)[:1000])
    print("==========================\n")
    return result


@app.post("/export-pdf")
async def export_pdf(result: dict):
    pdf_bytes = generate_pdf_report(result)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=report.pdf"},
    )


@app.get("/health")
async def health():
    return {"status": "ok", "model": "llama-3.3-70b-versatile"}