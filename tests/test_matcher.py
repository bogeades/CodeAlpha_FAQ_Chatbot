"""
Pytest Test Suite for CodeAlpha FAQ Chatbot NLP Engine.
"""

import pytest
from nlp.matcher import FAQMatcher
from nlp.preprocessor import TextPreprocessor


@pytest.fixture(scope="module")
def matcher():
    return FAQMatcher()


@pytest.fixture(scope="module")
def preprocessor():
    return TextPreprocessor()


def test_preprocessor_cleaning(preprocessor):
    raw = "Hello World! Check out https://codealpha.tech/ -- it's awesome."
    cleaned = preprocessor.clean_text(raw)
    assert "https" not in cleaned
    assert "hello world" in cleaned


def test_preprocessor_typo_correction(preprocessor):
    typo_text = "my submited projcet for the internshp"
    cleaned = preprocessor.clean_text(typo_text)
    assert "submitted" in cleaned
    assert "project" in cleaned
    assert "internship" in cleaned


def test_canonical_question_matching(matcher):
    res = matcher.match("What is the duration of the CodeAlpha internship?")
    assert res["success"] is True
    assert res["faq_id"] == "faq_002"
    assert res["confidence_score"] >= 0.7


def test_paraphrased_matching(matcher):
    res = matcher.match("How many weeks does the internship take?")
    assert res["success"] is True
    assert res["faq_id"] == "faq_002"


def test_typo_resilience(matcher):
    res = matcher.match("When do i get my certifcate?")
    assert res["success"] is True
    assert res["faq_id"] == "faq_010"
    assert res["is_fallback"] is False


def test_out_of_scope_fallback(matcher):
    res = matcher.match("Can I order a pepperoni pizza from you?")
    assert res["is_fallback"] is True
    assert res["confidence_score"] < matcher.default_threshold
    assert len(res["suggested_questions"]) > 0


def test_gibberish_handling(matcher):
    res = matcher.match("ajskdhasjkdhasjkdh zzz")
    assert res["is_fallback"] is True
    assert res["confidence_score"] == 0.0
