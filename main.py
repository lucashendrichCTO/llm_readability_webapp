from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from typing import List
from tempfile import NamedTemporaryFile
from docx import Document
import docx2txt

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def extract_text_from_docx(file_path):
    try:
        doc = Document(file_path)
        return " ".join([para.text for para in doc.paragraphs])
    except Exception:
        return docx2txt.process(file_path)

def extract_text_from_doc(file_path):
    # docx2txt can sometimes handle .doc files, else placeholder
    try:
        return docx2txt.process(file_path)
    except Exception:
        return "(Could not extract text)"

def llm_readability_score(text: str) -> float:
    # Placeholder: replace with LLM integration
    # For now, use a simple metric (Flesch Reading Ease)
    import textstat
    return textstat.flesch_reading_ease(text)

def readability_suggestions(score):
    """Return suggestions and examples based on Flesch Reading Ease score."""
    suggestions = []
    if score > 80:
        suggestions.append({
            "text": "Excellent readability. Consider using more advanced vocabulary if your audience allows.",
            "example": "Instead of 'good', try 'exceptional' or 'superb'."
        })
    if score <= 80:
        suggestions.append({
            "text": "Use shorter sentences and simpler words where possible.",
            "example": "Replace: 'The implementation of the new policy was met with considerable resistance.'\nWith: 'Many people resisted the new policy.'"
        })
    if score <= 60:
        suggestions.append({
            "text": "Break up long paragraphs. Use bullet points or lists.",
            "example": "Replace: 'The process involves several steps. First, gather data. Next, analyze the results. Then, write a report.'\nWith:\n- Gather data\n- Analyze results\n- Write a report"
        })
    if score <= 40:
        suggestions.append({
            "text": "Use active voice. Avoid jargon and complex constructions.",
            "example": "Replace: 'The experiment was conducted by the team.'\nWith: 'The team conducted the experiment.'"
        })
    if score <= 20:
        suggestions.append({
            "text": "Consider rewriting sentences for clarity. Use more familiar words.",
            "example": "Replace: 'Utilize' with 'use'; 'commence' with 'start'."
        })
    return suggestions

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "results": None})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(request: Request, files: List[UploadFile] = File(...)):
    results = []
    suggestions = []
    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()
        with NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        if ext == ".docx":
            text = extract_text_from_docx(tmp_path)
        elif ext == ".doc":
            text = extract_text_from_doc(tmp_path)
        else:
            text = "(Unsupported file type)"
        score = llm_readability_score(text) if text else 0
        results.append({"filename": file.filename, "score": score})
        suggestions.extend(readability_suggestions(score))
        os.remove(tmp_path)
    # Sort by score descending (higher = easier to read)
    results.sort(key=lambda x: x["score"], reverse=True)
    # Remove duplicate suggestions by text
    seen = set()
    unique_suggestions = []
    for s in suggestions:
        if s["text"] not in seen:
            unique_suggestions.append(s)
            seen.add(s["text"])
    return templates.TemplateResponse("index.html", {"request": request, "results": results, "suggestions": unique_suggestions})
