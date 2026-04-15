from dataclasses import dataclass, field
from typing import Optional


# ── Valid choices ─────────────────────────────────────────────────

KNOWLEDGE_LEVELS = ["beginner", "intermediate", "expert", "student", "general"]
SUMMARY_STYLES   = ["concise", "detailed", "bullet_points", "narrative", "technical"]
SUMMARY_LENGTHS  = ["short", "medium", "long"]
LANGUAGES        = ["bengali"]   # expandable: add "hindi", "marathi", etc. later


# ── Data class ────────────────────────────────────────────────────

@dataclass
class UserProfile:
    knowledge_level: str = "general"      # how expert is the user
    summary_style: str   = "concise"      # what style of output they want
    summary_length: str  = "medium"       # short / medium / long
    language: str        = "bengali"      # target output language
    domain: str          = "general"      # e.g. science, law, tech, general
    feedback_history: list = field(default_factory=list)  # stores past ratings


# ── Builder ───────────────────────────────────────────────────────

def build_profile(
    knowledge_level: Optional[str] = None,
    summary_style: Optional[str]   = None,
    summary_length: Optional[str]  = None,
    language: Optional[str]        = None,
    domain: Optional[str]          = None,
) -> UserProfile:
    """
    Construct a UserProfile from user-submitted form values.
    Falls back to defaults for any missing or invalid field.

    Args:
        knowledge_level: One of KNOWLEDGE_LEVELS
        summary_style:   One of SUMMARY_STYLES
        summary_length:  One of SUMMARY_LENGTHS
        language:        One of LANGUAGES
        domain:          Free-text domain (science, law, tech, etc.)

    Returns:
        Validated UserProfile instance.
    """
    return UserProfile(
        knowledge_level = knowledge_level if knowledge_level in KNOWLEDGE_LEVELS else "general",
        summary_style   = summary_style   if summary_style   in SUMMARY_STYLES   else "concise",
        summary_length  = summary_length  if summary_length  in SUMMARY_LENGTHS  else "medium",
        language        = language        if language        in LANGUAGES         else "bengali",
        domain          = domain or "general",
    )


# ── Prompt-building helpers ───────────────────────────────────────

def get_personalization_instruction(profile: UserProfile) -> str:
    """
    Returns a natural-language instruction that tells the summarizer
    how to adapt the summary for this user.

    This string is injected into the LLM summarizer prompt.
    """
    level_instructions = {
        "beginner":     "Use simple words and short sentences. Avoid technical jargon.",
        "intermediate": "Use clear language. Briefly explain technical terms if used.",
        "expert":       "Use precise technical language. Be concise and dense.",
        "student":      "Write clearly with key concepts highlighted. Suitable for studying.",
        "general":      "Write for a general adult reader. Clear and accessible.",
    }

    style_instructions = {
        "concise":       "Keep the summary brief and to the point.",
        "detailed":      "Include important supporting details and context.",
        "bullet_points": "Present the summary as a clear list of bullet points.",
        "narrative":     "Write the summary as flowing prose, like a short article.",
        "technical":     "Focus on technical details, methods, and precise facts.",
    }

    length_instructions = {
        "short":  "The summary should be very short (2-3 sentences or ~80 tokens).",
        "medium": "The summary should be moderate length (a short paragraph).",
        "long":   "The summary can be detailed and longer (3-5 paragraphs).",
    }

    parts = [
        f"Target audience: {profile.knowledge_level}.",
        level_instructions.get(profile.knowledge_level, ""),
        style_instructions.get(profile.summary_style, ""),
        length_instructions.get(profile.summary_length, ""),
    ]

    if profile.domain and profile.domain != "general":
        parts.append(f"The domain is {profile.domain}. Use appropriate terminology for this field.")

    return " ".join(p for p in parts if p)


def add_feedback(profile: UserProfile, rating: int, comment: str = "") -> None:
    """
    Append a feedback entry to the user's profile history.
    The critic agent reads this history to adjust future critiques.

    Args:
        profile: The UserProfile to update.
        rating:  Integer 1-5 (1 = poor summary, 5 = excellent).
        comment: Optional text feedback from the user.
    """
    profile.feedback_history.append({"rating": rating, "comment": comment})


def get_feedback_instruction(profile: UserProfile) -> str:
    """
    Summarise the user's feedback history into a short instruction
    that the critic agent can use to improve its critique.

    Returns an empty string if there is no feedback yet.
    """
    if not profile.feedback_history:
        return ""

    recent = profile.feedback_history[-5:]  # use last 5 feedbacks only
    avg_rating = sum(f["rating"] for f in recent) / len(recent)
    comments = [f["comment"] for f in recent if f.get("comment")]

    instruction = f"The user has previously rated summaries an average of {avg_rating:.1f}/5."

    if avg_rating < 3:
        instruction += " They seem unsatisfied — focus on making the summary clearer and more useful."
    elif avg_rating >= 4:
        instruction += " They have been satisfied with previous outputs — maintain this quality."

    if comments:
        instruction += " User comments: " + "; ".join(comments[-3:]) + "."

    return instruction