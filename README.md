# LLM Readability Analyzer Web App

A simple FastAPI web application to upload Word (.doc, .docx) documents and rank them by LLM-based readability (currently Flesch Reading Ease).

## Features
- Upload multiple .doc or .docx files
- Extracts text from Word documents
- Computes Flesch Reading Ease readability scores for each document
- Ranks documents by readability score
- Provides actionable suggestions to improve readability based on score
- Displays suggestions and examples in the UI
- Supports both .doc and .docx formats

## Getting Started
1. Install dependencies:
   ```
pip install -r requirements.txt
   ```
2. Run the app:
   ```
uvicorn main:app --reload
   ```
3. Open [http://localhost:8000](http://localhost:8000) in your browser.

## Notes
- For real LLM-based scoring, replace the `llm_readability_score` function in `main.py` with your preferred API call.
- Only .doc and .docx files are supported.
