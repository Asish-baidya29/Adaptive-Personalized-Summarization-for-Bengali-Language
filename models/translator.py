from __future__ import annotations
import logging
from typing import Optional

from transformers import pipeline, Pipeline

from config import config

logger = logging.getLogger(__name__)

# ── Lazy singleton ─────────────────────────────────────────────────
_translation_pipeline: Optional[Pipeline] = None


def _get_pipeline() -> Pipeline:
    """
    Load your fine-tuned English→Bengali translation model once.
    Supports both HuggingFace Hub models and locally saved models.
    """
    global _translation_pipeline
    if _translation_pipeline is None:
        if config.BENGALI_MODEL_SOURCE == "local":
            model_path = config.BENGALI_MODEL_LOCAL_PATH
            logger.info(f"Loading fine-tuned Bengali model from local path: {model_path}")
        else:
            model_path = config.BENGALI_MODEL
            logger.info(f"Loading Bengali translation model from HuggingFace Hub: {model_path}")

        _translation_pipeline = pipeline(
            task="translation",
            model=model_path,
            tokenizer=model_path,
            device=0 if _cuda_available() else -1,
        )
        logger.info("Bengali translation model loaded successfully.")
    return _translation_pipeline


# ── Public API ─────────────────────────────────────────────────────

def translate_to_bengali(english_summary: str) -> str:
    """
    Translate the final English summary into Bengali using your fine-tuned model.

    Args:
        english_summary: The refined English summary from the second-pass summarizer.

    Returns:
        Bengali translated string.
    """
    if not english_summary or not english_summary.strip():
        logger.warning("Empty summary passed to translator. Returning empty string.")
        return ""

    logger.info(f"Translating summary to Bengali ({len(english_summary.split())} words).")
    result = _get_pipeline()(
        english_summary,
        max_length=512,
        truncation=True,
    )

    translated = result[0]["translation_text"].strip()
    logger.info("Translation completed.")
    return translated


# ── Internal helpers ───────────────────────────────────────────────

def _cuda_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False