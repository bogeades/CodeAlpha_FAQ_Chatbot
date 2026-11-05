"""
FastAPI Server for CodeAlpha FAQ Chatbot.

Provides:
- REST API for querying the FAQ knowledge base (/api/chat)
- FAQ inspection and retrieval endpoints (/api/faqs, /api/suggested-questions)
- Health check (/api/health)
- Static file serving for the React frontend UI
"""

import os
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.schemas import ChatRequest, ChatResponse, FAQListResponse, HealthResponse
from nlp.matcher import FAQMatcher

# Initialize FastAPI application
app = FastAPI(
    title="CodeAlpha FAQ Chatbot API",
    description="Intelligent FAQ Chatbot powered by NLP (NLTK), TF-IDF, and Cosine Similarity.",
    version="1.0.0",
)

# Enable CORS for local development and cross-origin frontend support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root directory references
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"

# Initialize Matcher instance globally
matcher: FAQMatcher = None


@app.on_event("startup")
def startup_event():
    """Load FAQ dataset and train TF-IDF vectorizer at startup."""
    global matcher
    dataset_file = DATA_DIR / "faqs.json"
    if not dataset_file.exists():
        raise RuntimeError(f"FAQ dataset file missing at: {dataset_file}")
    matcher = FAQMatcher(dataset_path=str(dataset_file))


@app.get("/api/health", response_model=HealthResponse, tags=["System"])
def health_check() -> HealthResponse:
    """Return system health and active model metadata."""
    if not matcher:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Model initializing")

    return HealthResponse(
        status="healthy",
        service="CodeAlpha FAQ Chatbot NLP Engine",
        version="1.0.0",
        total_faqs_indexed=len(matcher.get_all_faqs()),
        default_threshold=matcher.default_threshold,
    )


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Process user question, compute similarity score, and return matching answer.
    Triggers fallback response if similarity is below the confidence threshold.
    """
    if not matcher:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Model initializing")

    result = matcher.match(
        query=request.message,
        threshold=request.threshold,
    )

    return ChatResponse(
        reply=result["answer"],
        confidence_score=result["confidence_score"],
        is_fallback=result["is_fallback"],
        matched_question=result.get("matched_question"),
        matched_pattern=result.get("matched_pattern"),
        category=result.get("category"),
        faq_id=result.get("faq_id"),
        threshold_used=result["threshold_used"],
        suggested_questions=result.get("suggested_questions", []),
    )


@app.get("/api/faqs", response_model=FAQListResponse, tags=["Knowledge Base"])
def get_faqs() -> FAQListResponse:
    """Retrieve full catalog of indexed FAQs and categories."""
    if not matcher:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Model initializing")

    faqs = matcher.get_all_faqs()
    categories = matcher.get_categories()

    return FAQListResponse(
        total=len(faqs),
        categories=categories,
        faqs=faqs,
        metadata=matcher.metadata,
    )


@app.get("/api/suggested-questions", tags=["Knowledge Base"])
def get_suggested_questions():
    """Retrieve starter conversation questions for frontend chips."""
    if not matcher:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Model initializing")

    return {
        "suggested_questions": matcher.get_quick_prompts()
    }


# Mount and serve static frontend files if directory exists
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", tags=["UI"])
    def serve_frontend_root():
        """Serve index.html at root url."""
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Frontend not found at expected location."}
