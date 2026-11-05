"""
FAQ Matching Engine using TF-IDF Vectorization and Cosine Similarity.

Handles:
- Corpus loading & indexing of questions + patterns
- scikit-learn TfidfVectorizer training with sublinear TF and n-grams
- Cosine similarity matrix computations
- Confidence threshold gating
- Intelligent fallback generation with suggested alternatives
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .preprocessor import TextPreprocessor, default_preprocessor


class FAQMatcher:
    """TF-IDF and Cosine Similarity FAQ Matching Engine."""

    def __init__(
        self,
        dataset_path: Optional[str] = None,
        preprocessor: Optional[TextPreprocessor] = None,
        default_threshold: float = 0.32,
    ):
        self.preprocessor = preprocessor or default_preprocessor
        self.dataset_path = (
            Path(dataset_path)
            if dataset_path
            else Path(__file__).resolve().parent.parent / "data" / "faqs.json"
        )
        self.default_threshold = default_threshold

        self.metadata: Dict[str, Any] = {}
        self.faqs: List[Dict[str, Any]] = []

        # Internal index structures
        self.corpus_texts: List[str] = []
        self.corpus_metadata: List[Dict[str, Any]] = []  # points back to FAQ object & pattern
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None

        self.load_dataset()
        self.train_vectorizer()

    def load_dataset(self) -> None:
        """Load and parse the JSON dataset."""
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"FAQ dataset not found at: {self.dataset_path}")

        with open(self.dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.metadata = data.get("metadata", {})
        self.faqs = data.get("faqs", [])
        if "default_threshold" in self.metadata:
            self.default_threshold = float(self.metadata["default_threshold"])

    def train_vectorizer(self) -> None:
        """
        Build and fit the TF-IDF vectorizer over canonical questions and patterns.
        Using (1, 2) n-grams allows capture of multi-word concepts like 'due date', 'lor letter'.
        """
        self.corpus_texts = []
        self.corpus_metadata = []

        for faq in self.faqs:
            # Index canonical question
            canonical_q = faq.get("question", "")
            preprocessed_canonical = self.preprocessor.preprocess(canonical_q)
            self.corpus_texts.append(preprocessed_canonical)
            self.corpus_metadata.append({
                "faq": faq,
                "pattern": canonical_q,
                "is_canonical": True,
            })

            # Index all pattern variations
            for pattern in faq.get("patterns", []):
                preprocessed_pat = self.preprocessor.preprocess(pattern)
                if preprocessed_pat and preprocessed_pat != preprocessed_canonical:
                    self.corpus_texts.append(preprocessed_pat)
                    self.corpus_metadata.append({
                        "faq": faq,
                        "pattern": pattern,
                        "is_canonical": False,
                    })

            # Index tags as searchable pattern
            tags_list = faq.get("tags", [])
            if tags_list:
                tags_str = " ".join(tags_list)
                preprocessed_tags = self.preprocessor.preprocess(tags_str)
                if preprocessed_tags:
                    self.corpus_texts.append(preprocessed_tags)
                    self.corpus_metadata.append({
                        "faq": faq,
                        "pattern": f"Keywords: {tags_str}",
                        "is_canonical": False,
                    })

        # Initialize TF-IDF Vectorizer
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            norm="l2",
            lowercase=False,  # Already normalized by our preprocessor
        )

        self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus_texts)

    def match(
        self,
        query: str,
        threshold: Optional[float] = None,
        top_k: int = 3,
    ) -> Dict[str, Any]:
        """
        Find the most relevant FAQ for a user query.

        Returns structured result with:
        - match found (bool)
        - answer
        - confidence_score
        - matched_question
        - category
        - fallback indicator
        - top alternatives
        """
        active_threshold = threshold if threshold is not None else self.default_threshold
        query_cleaned = query.strip()

        # Handle empty queries
        if not query_cleaned:
            fallback = self.metadata.get("fallback", {})
            return {
                "success": False,
                "is_fallback": True,
                "answer": "Please ask a question so I can assist you with your internship queries.",
                "confidence_score": 0.0,
                "matched_question": None,
                "category": None,
                "faq_id": None,
                "threshold_used": active_threshold,
                "suggested_questions": fallback.get("suggested_questions", []),
            }

        # Preprocess user query
        processed_query = self.preprocessor.preprocess(query_cleaned)

        # Handle queries that produced zero tokens after stopword/punct filtering
        if not processed_query:
            # Fall back to using cleaned text without stopword removal to catch small queries
            processed_query = self.preprocessor.clean_text(query_cleaned)

        query_vector = self.vectorizer.transform([processed_query])

        # If vector is empty (out of vocabulary completely)
        if query_vector.nnz == 0:
            fallback = self.metadata.get("fallback", {})
            return {
                "success": False,
                "is_fallback": True,
                "answer": fallback.get("message", "I'm sorry, I couldn't find an answer to your question."),
                "confidence_score": 0.0,
                "matched_question": None,
                "category": None,
                "faq_id": None,
                "threshold_used": active_threshold,
                "suggested_questions": fallback.get("suggested_questions", []),
            }

        # Calculate cosine similarity against all indexed questions/patterns
        sim_scores = cosine_similarity(query_vector, self.tfidf_matrix).flatten()

        # Group maximum scores by FAQ ID to consolidate pattern scores
        faq_scores: Dict[str, Tuple[float, Dict[str, Any], str]] = {}
        for idx, score in enumerate(sim_scores):
            meta = self.corpus_metadata[idx]
            faq = meta["faq"]
            faq_id = faq["id"]

            if faq_id not in faq_scores or score > faq_scores[faq_id][0]:
                faq_scores[faq_id] = (float(score), faq, meta["pattern"])

        # Sort FAQs by highest score
        ranked_faqs = sorted(faq_scores.values(), key=lambda x: x[0], reverse=True)

        if not ranked_faqs:
            fallback = self.metadata.get("fallback", {})
            return {
                "success": False,
                "is_fallback": True,
                "answer": fallback.get("message", "No matching FAQ found."),
                "confidence_score": 0.0,
                "matched_question": None,
                "category": None,
                "faq_id": None,
                "threshold_used": active_threshold,
                "suggested_questions": fallback.get("suggested_questions", []),
            }

        best_score, best_faq, best_pattern = ranked_faqs[0]
        confidence = round(float(best_score), 4)

        # Build top suggested alternatives (excluding the best match)
        alternatives = [
            f[1]["question"]
            for f in ranked_faqs[1 : top_k + 1]
            if f[0] > 0.15
        ]

        fallback_meta = self.metadata.get("fallback", {})

        # Confidence Threshold Decision
        if confidence >= active_threshold:
            return {
                "success": True,
                "is_fallback": False,
                "answer": best_faq["answer"],
                "confidence_score": confidence,
                "matched_question": best_faq["question"],
                "matched_pattern": best_pattern,
                "category": best_faq["category"],
                "faq_id": best_faq["id"],
                "threshold_used": active_threshold,
                "suggested_questions": alternatives or fallback_meta.get("suggested_questions", [])[:3],
            }
        else:
            # Below threshold -> trigger fallback response
            fallback_message = fallback_meta.get(
                "message",
                "I'm sorry, I couldn't find a confident answer to your question in our knowledge base.",
            )
            # Suggest highest potential matches or defaults
            suggestions = alternatives if alternatives else fallback_meta.get("suggested_questions", [])

            return {
                "success": False,
                "is_fallback": True,
                "answer": fallback_message,
                "confidence_score": confidence,
                "matched_question": best_faq["question"],
                "matched_pattern": best_pattern,
                "category": best_faq["category"],
                "faq_id": best_faq["id"],
                "threshold_used": active_threshold,
                "suggested_questions": suggestions[:3],
            }

    def get_all_faqs(self) -> List[Dict[str, Any]]:
        """Return all FAQs in the dataset."""
        return self.faqs

    def get_categories(self) -> List[str]:
        """Return unique categories."""
        return sorted(list({f["category"] for f in self.faqs}))

    def get_quick_prompts(self) -> List[str]:
        """Return starter questions for UI prompt pills."""
        prompts = [
            "What is the duration of the internship?",
            "What are the core tasks for the AI track?",
            "How do I submit my completed projects?",
            "When will I receive my certificate?",
            "Can I get a Letter of Recommendation?",
            "How do I fix NLTK resource not found errors?",
        ]
        return prompts
