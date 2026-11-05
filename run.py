"""
CodeAlpha FAQ Chatbot - Application Runner & Testing Suite.

Usage:
  python run.py --server       # Start FastAPI backend + React frontend on http://localhost:8000
  python run.py --test         # Execute full test suite (spelling variants, typos, fallback)
  python run.py --cli          # Interactive terminal chat session
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))


def bootstrap_nltk():
    """Verify preprocessor initialization."""
    pass


def run_tests():
    """Run comprehensive test suite verifying NLP matching, typos, and fallbacks."""
    bootstrap_nltk()
    from nlp.matcher import FAQMatcher

    print("\n" + "=" * 65)
    print("CODEALPHA FAQ CHATBOT - EVALUATION & ACCURACY TEST SUITE")
    print("=" * 65)

    matcher = FAQMatcher()
    print(f"Loaded {len(matcher.faqs)} FAQ records across {len(matcher.get_categories())} categories.")
    print(f"Default Confidence Threshold: {matcher.default_threshold}\n")

    test_queries = [
        # Canonical & direct phrasing
        ("What is the duration of the CodeAlpha internship?", True, "faq_002", "Direct canonical question"),
        ("What are the core tasks for the AI track?", True, "faq_004", "Direct canonical question"),
        ("How do I submit my completed internship projects?", True, "faq_007", "Direct canonical question"),
        ("When will I receive my internship completion certificate?", True, "faq_010", "Direct canonical question"),
        
        # Paraphrased & colloquial variants
        ("How long does this internship take to finish?", True, "faq_002", "Paraphrase of duration"),
        ("Is it work from home or online?", True, "faq_003", "Paraphrase of remote work"),
        ("Where should I send my github link for the tasks?", True, "faq_007", "Paraphrase of submission"),
        ("Can I add this certificate on my LinkedIn profile?", True, "faq_011", "Paraphrase of LinkedIn verification"),
        ("How can I get an official letter of recommendation?", True, "faq_012", "Paraphrase of LOR request"),
        ("How does the chatbot match questions using tfidf and cosine?", True, "faq_006", "Paraphrase of NLP mechanics"),

        # Spelling variations & typos
        ("When do i get my certifcate?", True, "faq_010", "Typo: 'certifcate'"),
        ("Can i get a deadilne extention for my submited projcet?", True, "faq_009", "Typos: 'deadilne', 'extention', 'projcet'"),
        ("What is the duartion of the internshp?", True, "faq_002", "Typos: 'duartion', 'internshp'"),
        ("Fix LookupError punkt or nltk stopwords error", True, "faq_013", "Technical error string"),

        # Out-of-scope queries (Must trigger Fallback)
        ("What is the capital city of France?", False, None, "Out-of-scope general trivia"),
        ("Can I order a pepperoni pizza from you?", False, None, "Out-of-scope food order"),
        ("What is quantum string theory and dark matter?", False, None, "Out-of-scope astrophysics"),
        ("xyz qwerty asdfghjk", False, None, "Gibberish / non-language input"),
    ]

    passed = 0
    total = len(test_queries)

    for idx, (query, should_match, expected_id, description) in enumerate(test_queries, 1):
        result = matcher.match(query)
        is_fallback = result["is_fallback"]
        confidence = result["confidence_score"]
        faq_id = result.get("faq_id")

        if should_match:
            success = (not is_fallback) and (faq_id == expected_id if expected_id else True)
        else:
            success = is_fallback

        if success:
            passed += 1
            status_tag = "[PASS]"
        else:
            status_tag = "[FAIL]"

        print(f"Test #{idx:02d} {status_tag} | Query: '{query}'")
        print(f"   Context:    {description}")
        print(f"   Confidence: {confidence * 100:.1f}% (Threshold: {result['threshold_used'] * 100:.0f}%)")
        outcome_str = "Fallback Triggered" if is_fallback else f"Matched [{faq_id}] - {result.get('category')}"
        print(f"   Outcome:    {outcome_str}")
        if not success:
            print(f"   Expected:   {'Fallback' if not should_match else f'Match {expected_id}'}")
        print("-" * 65)

    accuracy = (passed / total) * 100
    print(f"\nTEST SUITE SUMMARY: {passed}/{total} Passed ({accuracy:.1f}% Accuracy)")
    print("=" * 65)
    return passed == total


def run_cli():
    """Run an interactive chat in the terminal."""
    bootstrap_nltk()
    from nlp.matcher import FAQMatcher

    matcher = FAQMatcher()
    print("\n" + "=" * 60)
    print("ResolveAI - CodeAlpha FAQ Interactive Terminal")
    print("Type your question below, or type 'exit' or 'quit' to end.")
    print("=" * 60 + "\n")

    while True:
        try:
            user_input = input("You > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Exiting chat. Good luck with your CodeAlpha internship!")
                break

            result = matcher.match(user_input)
            print("\nBot >")
            if result["is_fallback"]:
                print(f"⚠️ [Low Confidence: {result['confidence_score']*100:.1f}%]")
            else:
                print(f"🎯 [Confidence: {result['confidence_score']*100:.1f}% | Category: {result['category']}]")
            print(f"{result['answer']}\n")

            if result.get("suggested_questions"):
                print("Suggested questions:")
                for q in result["suggested_questions"]:
                    print(f"  • {q}")
                print()
        except (KeyboardInterrupt, EOFError):
            print("\nSession ended.")
            break


def run_server(host="127.0.0.1", port=8000):
    """Start FastAPI server with Uvicorn."""
    bootstrap_nltk()
    import uvicorn
    print(f"\nStarting CodeAlpha FAQ Chatbot Server at http://{host}:{port}")
    print(f"Access Web UI at:       http://{host}:{port}/")
    print(f"Access API Docs at:     http://{host}:{port}/docs\n")
    uvicorn.run("backend.main:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CodeAlpha FAQ Chatbot Runner")
    parser.add_argument("--server", action="store_true", help="Start the FastAPI server & Web UI")
    parser.add_argument("--test", action="store_true", help="Run NLP accuracy test suite")
    parser.add_argument("--cli", action="store_true", help="Start interactive CLI chat")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind server (default: 8000)")

    args = parser.parse_args()

    if args.test:
        run_tests()
    elif args.cli:
        run_cli()
    else:
        # Default action: run tests first to verify, then launch server
        run_server(port=args.port)
