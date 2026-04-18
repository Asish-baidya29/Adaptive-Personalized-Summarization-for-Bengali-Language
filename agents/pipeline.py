import logging
import time
from typing import TypedDict

from utils.preprocessor import preprocess, get_doc_type_label
from utils.user_profile import (
    UserProfile,
    get_personalization_instruction,
    add_feedback,
)
from models.summarizer import generate_summary, generate_refined_summary
from models.translator import translate_to_bengali
from agents.critic_agent import critique_summary

logger = logging.getLogger(__name__)


# ── Result type ────────────────────────────────────────────────────

class PipelineResult(TypedDict):
    doc_type: str                # Detected document type (display label)
    word_count: int              # Word count of original
    estimated_reading_time: str  # e.g. "3 min read"
    initial_summary: str         # First-pass English summary
    critique: str                # Critic agent feedback
    refined_summary: str         # Second-pass English summary
    bengali_output: str          # Final Bengali translated summary
    elapsed_seconds: float       # Total pipeline processing time


# ── Public API ─────────────────────────────────────────────────────

def run_pipeline(raw_text: str, user_profile: UserProfile) -> PipelineResult:
    """
    Execute the full summarization pipeline from raw input to Bengali output.

    Args:
        raw_text:     The English text entered/uploaded by the user.
        user_profile: The user's preferences (built by utils/user_profile.py).

    Returns:
        PipelineResult dict containing all intermediate and final outputs.
    """
    start_time = time.time()

    # ── Step 1: Preprocess ─────────────────────────────────────────
    logger.info("Step 1: Preprocessing input text.")
    doc = preprocess(raw_text)

    # ── Step 2: Build personalization instruction ──────────────────
    logger.info("Step 2: Building personalization instruction.")
    personalization = get_personalization_instruction(user_profile)

    # ── Step 3: First-pass summary ─────────────────────────────────
    logger.info("Step 3: Generating first-pass summary.")
    initial_summary = generate_summary(
        cleaned_text=doc["cleaned_text"],
        personalization_instruction=personalization,
        summary_length=user_profile.summary_length,
    )

    # ── Step 4: Critic agent ───────────────────────────────────────
    logger.info("Step 4: Critic agent evaluating summary.")
    critique = critique_summary(
        original_text=doc["cleaned_text"],
        user_profile=user_profile,
        initial_summary=initial_summary,
    )

    # ── Step 5: Refined summary ────────────────────────────────────
    logger.info("Step 5: Generating refined summary based on critique.")
    refined_summary = generate_refined_summary(
        cleaned_text=doc["cleaned_text"],
        personalization_instruction=personalization,
        critic_feedback=critique,
        summary_length=user_profile.summary_length,
    )

    # ── Step 6: Translate to Bengali ───────────────────────────────
    logger.info("Step 6: Translating refined summary to Bengali.")
    bengali_output = translate_to_bengali(refined_summary)

    elapsed = round(time.time() - start_time, 2)
    logger.info(f"Pipeline completed in {elapsed}s.")

    return PipelineResult(
        doc_type=get_doc_type_label(doc["doc_type"]),
        word_count=doc["word_count"],
        estimated_reading_time=doc["estimated_reading_time"],
        initial_summary=initial_summary,
        critique=critique,
        refined_summary=refined_summary,
        bengali_output=bengali_output,
        elapsed_seconds=elapsed,
    )


def apply_user_feedback(user_profile: UserProfile, rating: int, comment: str = "") -> None:
    """
    Store user feedback into the profile so the critic agent can use it next time.

    Args:
        user_profile: The current user's profile object.
        rating:       Integer 1–5.
        comment:      Optional text feedback.
    """
    add_feedback(user_profile, rating, comment)
    logger.info(f"User feedback recorded: rating={rating}, comment={repr(comment)}")