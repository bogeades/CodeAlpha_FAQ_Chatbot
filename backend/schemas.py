"""
Pydantic data schemas for request validation and response serialization.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User input message or question")
    threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Optional custom similarity threshold override")
    conversation_id: Optional[str] = Field(None, description="Optional client session or conversation identifier")


class ChatResponse(BaseModel):
    reply: str = Field(..., description="Chatbot generated answer or fallback response")
    confidence_score: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")
    is_fallback: bool = Field(..., description="True if similarity score fell below threshold")
    matched_question: Optional[str] = Field(None, description="Canonical question matched in dataset")
    matched_pattern: Optional[str] = Field(None, description="Exact pattern/variation closest to user query")
    category: Optional[str] = Field(None, description="FAQ category of matched question")
    faq_id: Optional[str] = Field(None, description="Unique FAQ identifier")
    threshold_used: float = Field(..., description="Threshold evaluated for this decision")
    suggested_questions: List[str] = Field(default_factory=list, description="Follow-up or alternative suggestions")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class FAQItem(BaseModel):
    id: str
    category: str
    question: str
    patterns: List[str] = Field(default_factory=list)
    answer: str
    tags: List[str] = Field(default_factory=list)


class FAQListResponse(BaseModel):
    total: int
    categories: List[str]
    faqs: List[FAQItem]
    metadata: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    total_faqs_indexed: int
    default_threshold: float
