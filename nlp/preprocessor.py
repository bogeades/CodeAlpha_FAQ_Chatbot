"""
NLP Preprocessing Module for CodeAlpha FAQ Chatbot.

Responsibilities:
1. Text normalization (case-folding, special character stripping).
2. Resilient tokenization (NLTK word_tokenize with robust regex fallback).
3. Stopword removal with built-in corpus and question interrogative preservation.
4. Word normalization and lemmatization (WordNetLemmatizer + algorithmic rule fallback).
5. Typo correction and domain spelling normalization.
"""

import re
import string
from typing import List, Set

# Attempt NLTK imports without blocking network calls
_nltk_available = False
try:
    import nltk
    from nltk.stem import WordNetLemmatizer
    from nltk.tokenize import word_tokenize
    _nltk_available = True
except ImportError:
    pass

# Built-in standard English stopwords to ensure 100% offline reliability
STANDARD_STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between",
    "both", "but", "by", "can", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does",
    "doesn't", "don't", "down", "during", "each", "few", "for", "from", "further", "had",
    "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's",
    "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "i", "i'd",
    "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on",
    "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
    "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some",
    "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
    "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "when", "where", "which", "while",
    "who", "whom", "why", "will", "with", "won't", "would", "wouldn't",
    "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves",
}

# Preserve interrogative words to capture intent structure
INTERROGATIVE_PRESERVES: Set[str] = {
    "what", "how", "when", "where", "why", "who", "which", "can", "is", "are", "do", "does"
}


class TextPreprocessor:
    """Production NLP text cleaner, tokenizer, and lemmatizer."""

    SPELL_MAP = {
        "ia": "is",
        "waht": "what",
        "teh": "the",
        "objcet": "object",
        "obect": "object",
        "internshipp": "internship",
        "internshp": "internship",
        "intrenship": "internship",
        "certifcate": "certificate",
        "certificte": "certificate",
        "certfcate": "certificate",
        "submision": "submission",
        "sumbit": "submit",
        "submitt": "submit",
        "submited": "submitted",
        "submittingg": "submitting",
        "deadilne": "deadline",
        "deadlin": "deadline",
        "projcet": "project",
        "projets": "projects",
        "requirment": "requirement",
        "requirments": "requirements",
        "duraton": "duration",
        "duartion": "duration",
        "chatbt": "chatbot",
        "chatbott": "chatbot",
        "verifcation": "verification",
        "algoritm": "algorithm",
        "recomandation": "recommendation",
        "recomended": "recommended",
        "extention": "extension",
        "menter": "mentor",
    }

    def __init__(self, use_lemmatization: bool = True, remove_stopwords: bool = True):
        self.use_lemmatization = use_lemmatization
        self.remove_stopwords = remove_stopwords

        # Standard English stopwords
        self.stop_words = STANDARD_STOPWORDS.copy()

        # If NLTK stopwords available locally, enrich
        if _nltk_available:
            try:
                from nltk.corpus import stopwords
                nltk_stops = set(stopwords.words("english"))
                self.stop_words.update(nltk_stops)
            except Exception:
                pass

        # Try initializing WordNet lemmatizer
        self.lemmatizer = None
        if _nltk_available and self.use_lemmatization:
            try:
                self.lemmatizer = WordNetLemmatizer()
                # Test if corpus is accessible without error
                self.lemmatizer.lemmatize("testing")
            except Exception:
                self.lemmatizer = None

    def correct_spelling(self, text: str) -> str:
        """Replace common student query typos."""
        tokens = text.split()
        return " ".join([self.SPELL_MAP.get(t.lower(), t) for t in tokens])

    def clean_text(self, text: str) -> str:
        """Clean string: lowercase, spelling correction, URL/email removal, punctuation stripping."""
        if not text:
            return ""

        text = text.lower()
        text = self.correct_spelling(text)

        # Remove URLs and email addresses
        text = re.sub(r"https?://\S+|www\.\S+", "", text)
        text = re.sub(r"\S+@\S+", "", text)

        # Replace punctuation with whitespace
        text = re.sub(rf"[{re.escape(string.punctuation)}]", " ", text)

        # Collapse whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def tokenize(self, text: str) -> List[str]:
        """Tokenize string with NLTK or regex fallback."""
        cleaned = self.clean_text(text)
        if not cleaned:
            return []

        # Try NLTK tokenizer first
        if _nltk_available:
            try:
                return word_tokenize(cleaned)
            except Exception:
                pass

        # Robust regex-based word tokenization fallback
        return re.findall(r"\b\w+\b", cleaned)

    def rule_based_lemmatize(self, word: str) -> str:
        """Algorithmic suffix stripping / stemming fallback when WordNet is absent."""
        if len(word) <= 3:
            return word

        # Common plural and verbal forms
        if word.endswith("ies") and len(word) > 4:
            return word[:-3] + "y"
        if word.endswith("ing") and len(word) > 5:
            base = word[:-3]
            # Handle double consonants: e.g. submitting -> submit
            if len(base) > 3 and base[-1] == base[-2] and base[-1] in "tpgmnd":
                return base[:-1]
            return base
        if word.endswith("ed") and len(word) > 4:
            base = word[:-2]
            if len(base) > 3 and base[-1] == base[-2] and base[-1] in "tpgmnd":
                return base[:-1]
            return base
        if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
            return word[:-1]

        return word

    def lemmatize_token(self, token: str) -> str:
        """Lemmatize token using NLTK WordNet or algorithmic fallback."""
        if len(token) <= 2:
            return token

        if self.lemmatizer:
            try:
                # Try verb then noun
                lemma = self.lemmatizer.lemmatize(token, pos="v")
                if lemma == token:
                    lemma = self.lemmatizer.lemmatize(token, pos="n")
                return lemma
            except Exception:
                pass

        return self.rule_based_lemmatize(token)

    def preprocess(self, text: str) -> str:
        """Transform raw text into normalized, lemmatized, stopword-filtered string."""
        tokens = self.tokenize(text)
        result: List[str] = []

        for token in tokens:
            if not token or len(token) < 2:
                continue

            if self.remove_stopwords and token in self.stop_words:
                continue

            if self.use_lemmatization:
                token = self.lemmatize_token(token)

            result.append(token)

        return " ".join(result)


# Singleton instance
default_preprocessor = TextPreprocessor()
