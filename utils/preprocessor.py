import re
from typing import TypedDict


# ── Type for preprocessed output ──────────────────────────────────
class PreprocessedDoc(TypedDict):
    cleaned_text: str         
    doc_type: str              
    word_count: int            
    char_count: int            
    estimated_reading_time: str  


# ── Document-type detection rules ─────────────────────────────────

_DOC_TYPE_RULES = [
    ("research_paper", [
        "abstract", "introduction", "methodology", "conclusion",
        "references", "doi", "et al", "hypothesis", "experiment",
        "results", "discussion", "literature review", "citation",
    ]),
    ("news_article", [
        "reported", "according to", "spokesperson", "breaking",
        "journalist", "editorial", "published", "press release",
        "correspondent", "wire", "reuters", "ap news",
    ]),
    ("story_novel", [
        "chapter", "once upon", "narrator", "protagonist", "dialogue",
        "he said", "she said", "they said", "the story", "fiction",
        "plot", "character", "setting", "climax",
    ]),
    ("question_answer", [
        "question:", "answer:", "q:", "a:", "faq", "what is", "how do",
        "why does", "explain", "define", "what are the steps",
    ]),
    ("blog_post", [
        "in this post", "in this article", "subscribe", "follow us",
        "comment below", "read more", "blog", "tutorial", "step by step",
    ]),
]

_GENERAL_LABEL = "general"


# ── Public API ─────────────────────────────────────────────────────

def preprocess(raw_text: str) -> PreprocessedDoc:
    """
    Clean the input text and detect its document type.

    Args:
        raw_text: Any English text pasted or uploaded by the user.

    Returns:
        PreprocessedDoc with cleaned text, detected type, and metadata.
    """
    cleaned = _clean_text(raw_text)
    doc_type = _detect_doc_type(cleaned)
    word_count = len(cleaned.split())
    char_count = len(cleaned)
    reading_time = _estimate_reading_time(word_count)

    return PreprocessedDoc(
        cleaned_text=cleaned,
        doc_type=doc_type,
        word_count=word_count,
        char_count=char_count,
        estimated_reading_time=reading_time,
    )


def get_doc_type_label(doc_type: str) -> str:
    """
    Return a human-friendly label for display in the UI.
    """
    labels = {
        "research_paper": "Research Paper",
        "news_article":   "News Article",
        "story_novel":    "Story / Novel",
        "question_answer": "Question & Answer",
        "blog_post":      "Blog Post",
        "general":        "General Document",
    }
    return labels.get(doc_type, "General Document")


# ── Internal helpers ───────────────────────────────────────────────

def _clean_text(text: str) -> str:
    """Remove extra whitespace, normalize unicode, strip HTML tags."""
    # Strip basic HTML tags (if user pastes from a webpage)
    text = re.sub(r"<[^>]+>", " ", text)
    # Normalize unicode quotes and dashes
    text = text.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "--")
    # Collapse multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse multiple spaces
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def _detect_doc_type(text: str) -> str:
    """
    Score the text against keyword signals for each document type.
    Returns the type with the highest signal count, or 'general'.
    """
    lower = text.lower()
    best_label = _GENERAL_LABEL
    best_score = 0

    for label, keywords in _DOC_TYPE_RULES:
        score = sum(1 for kw in keywords if kw in lower)
        if score > best_score:
            best_score = score
            best_label = label

    return best_label


def _estimate_reading_time(word_count: int) -> str:
    """
    Estimate reading time assuming 200 words per minute (average adult).
    Returns a human-readable string like '3 min read'.
    """
    minutes = max(1, round(word_count / 200))
    return f"{minutes} min read"