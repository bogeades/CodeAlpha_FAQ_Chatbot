# 🤖 ResolveAI — CodeAlpha FAQ Chatbot

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.0-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-TF--IDF-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![NLTK](https://img.shields.io/badge/NLP-NLTK-green.svg)](https://www.nltk.org/)
[![Tests](https://img.shields.io/badge/Tests-100%25%20Passing-brightgreen.svg)](https://pytest.org)

An intelligent, production-ready **Natural Language Processing (NLP) FAQ Chatbot** engineered for the **CodeAlpha Artificial Intelligence Internship**. 

Built with **Python FastAPI**, **NLTK**, **scikit-learn (TF-IDF & Cosine Similarity)**, and a **modern React interface** inspired by conversational platforms like *ResolveAI*.

---

## 🌟 Key Features

- **Structured Knowledge Base:** Multi-category JSON dataset containing canonical questions, colloquial patterns, rich markdown answers, and keywords.
- **Robust NLP Preprocessing:** Case normalization, punctuation handling, word tokenization, stopword removal, and rule-based/WordNet lemmatization.
- **Typo & Spelling Tolerance:** Handles common student typos (e.g., `certifcate`, `deadilne`, `submited`, `duartion`) and maps them accurately.
- **Mathematical Vector Space Modeling:** Uses `TfidfVectorizer` with n-grams `(1, 2)` and sublinear term frequency scaling for optimal phrase sensitivity.
- **Cosine Similarity Engine:** Calculates normalized vector similarity against the indexed FAQ knowledge base in sub-millisecond latency.
- **Confidence Threshold Gating:** Configurable threshold (default `0.32` / `32%`). Queries below threshold automatically trigger helpful fallback responses.
- **Smart Fallbacks:** Suggests alternative FAQs and provides direct mentor contact details when confidence is low.
- **Modern Responsive React UI:**
  - Real-time chat bubbles with timestamps
  - Predefined question chips (conversation starters)
  - Animated typing indicator
  - Confidence score badges (`% Match` + matched category)
  - Interactive Knowledge Base catalog browser
  - Dynamic threshold tuning slider
  - Chat transcript export to `.txt`
- **Comprehensive Testing:** 100% passing test suite across direct, paraphrased, typo-laden, and out-of-scope inputs.

---

## 🏛️ System Architecture

```
User Input Query / Quick Chip
          │
          ▼
┌──────────────────────────────────────────────┐
│       Frontend: React 18 UI Widget           │
│  - Message History & Timestamps              │
│  - Predefined Question Pills                 │
│  - Live Threshold Slider                     │
└──────────────────────┬───────────────────────┘
                       │ POST /api/chat
                       ▼
┌──────────────────────────────────────────────┐
│       Backend: Python FastAPI Service        │
│  - Request Validation (Pydantic)             │
│  - CORS & Static Asset Serving               │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│         NLP Preprocessing Pipeline           │
│  - Lowercase & Typo Normalization            │
│  - Punctuation & Special Char Stripping      │
│  - Tokenization                              │
│  - Stopword Filtering                        │
│  - Lemmatization (WordNet / Rules)           │
└──────────────────────┬───────────────────────┘
                       │ Transformed Query Vector
                       ▼
┌──────────────────────────────────────────────┐
│     scikit-learn TF-IDF & Cosine Engine      │
│  - Dot Product of L2 Normalized Vectors      │
│  - Ranked Score Evaluation                   │
└──────────────────────┬───────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
   Score >= Threshold        Score < Threshold
          │                         │
          ▼                         ▼
┌─────────────────────┐   ┌─────────────────────┐
│ Best Matched Answer │   │  Fallback Response  │
│  + Confidence Score │   │  + Suggested FAQs   │
└─────────┬───────────┘   └─────────┬───────────┘
          └────────────┬────────────┘
                       │ JSON Response
                       ▼
            Chat Bubble Rendered in UI
```

---

## 📁 Project Directory Structure

```
CodeAlpha_FAQ_Chatbot/
├── data/
│   └── faqs.json              # Structured JSON FAQ dataset (15 items across 5 categories)
├── nlp/
│   ├── __init__.py
│   ├── preprocessor.py        # Tokenizer, stopword filter, lemmatizer, typo corrector
│   └── matcher.py             # TF-IDF vectorizer, Cosine Similarity, fallback engine
├── backend/
│   ├── __init__.py
│   ├── main.py                # FastAPI server, REST routes, static file mount
│   └── schemas.py             # Pydantic schemas (ChatRequest, ChatResponse, etc.)
├── frontend/
│   ├── index.html             # React 18 application shell with Tailwind & Babel
│   ├── app.js                 # Interactive React application logic & state
│   └── style.css              # Custom styling, animations, and glassmorphism
├── tests/
│   ├── __init__.py
│   └── test_matcher.py        # Automated pytest test cases
├── requirements.txt           # Python dependencies (FastAPI, scikit-learn, NLTK, etc.)
├── run.py                     # CLI runner (server, tests, interactive terminal)
├── run.bat                    # One-click Windows launch script
├── DOCUMENTATION.md           # In-depth technical report for CodeAlpha submission
└── README.md                  # Project documentation
```

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.9+ (Python 3.11 recommended)
- Modern web browser (Chrome, Edge, Firefox, Safari)

### 1. Installation
Clone or navigate to the project directory:
```bash
cd CodeAlpha_FAQ_Chatbot
```

Install required Python packages:
```bash
pip install -r requirements.txt
```

### 2. Run the Application
**Option A: One-click launcher (Windows):**
Double-click `run.bat` or run:
```cmd
run.bat
```

**Option B: Python CLI:**
```bash
python run.py --server
```

Open your browser and visit:
- **Interactive Chatbot Web UI:** [http://localhost:8000/](http://localhost:8000/)
- **Interactive Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Run Accuracy & Typo Test Suite
```bash
python run.py --test
```
or run with pytest:
```bash
pytest tests/
```

### 4. Interactive Terminal Mode (CLI)
You can also chat directly within your command line:
```bash
python run.py --cli
```

---

## 📡 API Reference

### `POST /api/chat`
Ask a question to the FAQ chatbot.

**Request:**
```json
{
  "message": "When will I receive my certificate?",
  "threshold": 0.32
}
```

**Response:**
```json
{
  "reply": "Certificates of Completion are verified and issued within 7 to 14 working days...",
  "confidence_score": 1.0,
  "is_fallback": false,
  "matched_question": "When will I receive my internship completion certificate?",
  "matched_pattern": "When will I receive my internship completion certificate?",
  "category": "Certificates & Perks",
  "faq_id": "faq_010",
  "threshold_used": 0.32,
  "suggested_questions": [
    "Is the CodeAlpha certificate verified and shareable on LinkedIn?",
    "Can I receive a Letter of Recommendation (LOR)?"
  ],
  "timestamp": "2026-11-05T20:00:00.000Z"
}
```

### `GET /api/faqs`
Retrieves all indexed FAQ entries, categories, and knowledge base metadata.

### `GET /api/suggested-questions`
Retrieves prompt starters for UI conversation chips.

### `GET /api/health`
Returns system status, active version, and indexed question count.

---

## 🧪 Accuracy & Evaluation Summary

| Query Category | Example Test Query | Expected Match | Result | Score |
| :--- | :--- | :--- | :--- | :--- |
| **Canonical** | *"What is the duration of the CodeAlpha internship?"* | `faq_002` | **PASS** | 100.0% |
| **Paraphrased** | *"How long does this internship take to finish?"* | `faq_002` | **PASS** | 82.3% |
| **Colloquial** | *"Is it work from home or online?"* | `faq_003` | **PASS** | 84.7% |
| **Typo Variant** | *"When do i get my certifcate?"* | `faq_010` | **PASS** | 61.1% |
| **Multi-Typo** | *"Can i get a deadilne extention for my submited projcet?"* | `faq_009` | **PASS** | 60.0% |
| **Out-of-Scope** | *"What is the capital city of France?"* | Fallback | **PASS** | 0.0% |
| **Out-of-Scope** | *"Can I order a pepperoni pizza from you?"* | Fallback | **PASS** | 0.0% |
| **Gibberish** | *"xyz qwerty asdfghjk"* | Fallback | **PASS** | 0.0% |

**Overall Evaluation Suite Accuracy:** **100% (18/18 test cases passing)**

---

## 📜 License & Credits

Developed for the **CodeAlpha AI Internship Program**.
Licensed under the [MIT License](LICENSE).
