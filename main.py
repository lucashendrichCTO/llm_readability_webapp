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
    # Calculate a score based on factors that make text easier for LLMs to process
    # Higher score = better for LLM training and inference
    import re
    import math
    from collections import Counter
    
    # Initialize score at 40 (below average) - must earn points to reach higher levels
    score = 40.0
    
    # Empty text gets zero score
    if not text or len(text.strip()) == 0:
        return 0
    
    # Split into sentences and words
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = re.findall(r'\b\w+\b', text.lower())
    
    # 1. Sentence length - moderate length sentences (12-20 words) are optimal for LLMs
    # More stringent range than before
    avg_sentence_length = len(words) / max(1, len(sentences))
    if 12 <= avg_sentence_length <= 20:
        score += 10
    elif 8 <= avg_sentence_length < 12 or 20 < avg_sentence_length <= 25:
        score += 5  # Partial points for close to optimal
    elif avg_sentence_length < 5 or avg_sentence_length > 35:
        score -= 15  # Bigger penalty for extremes
    
    # 2. Vocabulary diversity - moderate diversity is good (not too repetitive, not too diverse)
    # Narrower optimal range
    unique_words = len(set(words))
    diversity_ratio = unique_words / max(1, len(words))
    if 0.35 <= diversity_ratio <= 0.55:
        score += 12
    elif 0.25 <= diversity_ratio < 0.35 or 0.55 < diversity_ratio <= 0.65:
        score += 6  # Partial points
    elif diversity_ratio > 0.75:  # Too many unique words
        score -= 12
    elif diversity_ratio < 0.2:  # Too repetitive
        score -= 10
    
    # 3. Structure - well-structured text with paragraphs is better for LLMs
    paragraphs = text.split('\n\n')
    if 4 <= len(paragraphs) <= 12:
        score += 10
    elif 2 <= len(paragraphs) < 4 or 12 < len(paragraphs) <= 20:
        score += 5  # Partial points
    elif len(paragraphs) > 25 or len(paragraphs) == 1:
        score -= 8  # Penalty for poor structure
    
    # 4. Repetition patterns - some repetition helps LLMs learn patterns
    word_counts = Counter(words)
    common_words = [word for word, count in word_counts.most_common(10)]
    common_word_ratio = sum(word_counts[word] for word in common_words) / max(1, len(words))
    if 0.15 <= common_word_ratio <= 0.25:
        score += 12
    elif 0.1 <= common_word_ratio < 0.15 or 0.25 < common_word_ratio <= 0.3:
        score += 6  # Partial points
    elif common_word_ratio > 0.4:  # Too repetitive
        score -= 10
    
    # 5. Special characters and formatting
    special_chars_ratio = len(re.findall(r'[^\w\s]', text)) / max(1, len(text))
    if special_chars_ratio <= 0.05:  # Minimal special characters
        score += 8
    elif 0.05 < special_chars_ratio <= 0.08:
        score += 4  # Partial points
    elif special_chars_ratio > 0.12:  # Too many special characters
        score -= 15
    
    # 6. Sentence complexity - analyze clause structure (new metric)
    complex_sentence_markers = ['although', 'though', 'while', 'whereas', 'because', 
                               'since', 'unless', 'if', 'when', 'whenever', 'where', 
                               'whereby', 'that', 'which', 'who', 'whom', 'whose']
    complex_sentence_count = sum(1 for word in words if word.lower() in complex_sentence_markers)
    complex_ratio = complex_sentence_count / max(1, len(sentences))
    
    if 0.2 <= complex_ratio <= 0.5:  # Good balance of simple and complex sentences
        score += 8
    elif complex_ratio > 0.7:  # Too many complex sentences
        score -= 10
    
    # 7. Consistency check - penalize inconsistent capitalization and formatting
    capitalized_words = sum(1 for word in re.findall(r'\b\w+\b', text) if word[0].isupper())
    capitalization_ratio = capitalized_words / max(1, len(words))
    if capitalization_ratio > 0.3 and capitalization_ratio < 0.7:  # Inconsistent capitalization
        score -= 8
    
    # Ensure score is between 0 and 100
    return max(0, min(100, score))

def get_score_explanation(score):
    """Return an explanation of what the LLM readability score means."""
    if score >= 85:
        return {
            "level": "Exceptional for LLMs",
            "training_value": "Premium training data",
            "description": "This text has exceptional characteristics for LLM training and inference. Perfectly balanced structure, vocabulary, and complexity patterns."
        }
    elif score >= 75:
        return {
            "level": "Excellent for LLMs",
            "training_value": "High-quality training data",
            "description": "This content is excellently suited for LLMs. It has near-optimal structure, appropriate sentence complexity, and well-balanced vocabulary diversity."
        }
    elif score >= 65:
        return {
            "level": "Very Good for LLMs",
            "training_value": "Very valuable training data",
            "description": "This text works very well for LLM training and inference. It has strong patterns with only minor improvements possible."
        }
    elif score >= 55:
        return {
            "level": "Good for LLMs",
            "training_value": "Good training data",
            "description": "This content is good for LLMs but has some characteristics that could be improved for better model performance."
        }
    elif score >= 45:
        return {
            "level": "Moderately Good for LLMs",
            "training_value": "Useful training data",
            "description": "This text has moderately good characteristics for LLM processing. Several aspects could be improved for optimal results."
        }
    elif score >= 35:
        return {
            "level": "Average for LLMs",
            "training_value": "Basic training data",
            "description": "This content has average characteristics for LLM processing. It may have inconsistent structure, complexity, or vocabulary patterns."
        }
    elif score >= 25:
        return {
            "level": "Below Average for LLMs",
            "training_value": "Requires preprocessing",
            "description": "This text may be challenging for LLMs to process effectively. Consider restructuring with more consistent patterns."
        }
    else:
        return {
            "level": "Difficult for LLMs",
            "training_value": "Not ideal for training",
            "description": "This content has characteristics that make it difficult for LLMs to process effectively. Consider significant restructuring."
        }

def readability_suggestions(score):
    """Return suggestions and examples based on LLM readability score."""
    suggestions = []
    if score > 75:
        suggestions.append({
            "text": "Exceptional LLM-friendly content. Consider using as a gold standard template.",
            "example": "Your balanced sentence structure, optimal vocabulary diversity, and consistent patterns make this ideal for LLM processing."
        })
    if score <= 75:
        suggestions.append({
            "text": "Fine-tune sentence length distribution for optimal LLM processing.",
            "example": "Aim for sentences between 12-20 words. Current average may be outside the optimal range."
        })
    if score <= 65:
        suggestions.append({
            "text": "Optimize vocabulary diversity ratio (aim for 0.35-0.55 unique words ratio).",
            "example": "Your text may have too many unique terms or be too repetitive. Balance consistent terminology with controlled variation."
        })
    if score <= 55:
        suggestions.append({
            "text": "Improve paragraph structure and document organization.",
            "example": "Aim for 4-12 well-structured paragraphs with clear topical focus in each."
        })
    if score <= 45:
        suggestions.append({
            "text": "Balance simple and complex sentences (aim for 20-50% complex sentences).",
            "example": "Your text may have too many complex sentences with multiple clauses or too many overly simple sentences."
        })
    if score <= 35:
        suggestions.append({
            "text": "Reduce special characters and inconsistent formatting.",
            "example": "Minimize special characters to less than 5% of your text and maintain consistent capitalization patterns."
        })
    if score <= 25:
        suggestions.append({
            "text": "Consider complete restructuring with more consistent patterns and clearer organization.",
            "example": "Break very long paragraphs into smaller units, simplify overly complex sentences, and use more consistent terminology throughout."
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
        explanation = get_score_explanation(score)
        results.append({
            "filename": file.filename, 
            "score": score,
            "explanation": explanation
        })
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
