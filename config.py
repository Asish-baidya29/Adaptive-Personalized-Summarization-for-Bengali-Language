import os
from dotenv import load_dotenv

load_dotenv()  # reads .env file into os.environ


class Config:
    # ── HuggingFace ────────────────────────────────
    HUGGINGFACE_API_TOKEN: str = os.getenv("HUGGINGFACE_API_TOKEN", "")

    # ── Models ─────────────────────────────────────
    SUMMARIZER_MODEL: str = os.getenv("SUMMARIZER_MODEL", "facebook/bart-large-cnn")
    CRITIC_MODEL: str = os.getenv("CRITIC_MODEL", "google/flan-t5-large")
    BENGALI_MODEL: str = os.getenv("BENGALI_MODEL", "Helsinki-NLP/opus-mt-en-bn")
    BENGALI_MODEL_SOURCE: str = os.getenv("BENGALI_MODEL_SOURCE", "hub")  # "hub" or "local"
    BENGALI_MODEL_LOCAL_PATH: str = os.getenv("BENGALI_MODEL_LOCAL_PATH", "./models/eng_bengali_finetuned")

    # ── Summary Length Limits ──────────────────────
    MAX_SUMMARY_LENGTH = {
        "short":  int(os.getenv("MAX_SUMMARY_LENGTH_SHORT",  80)),
        "medium": int(os.getenv("MAX_SUMMARY_LENGTH_MEDIUM", 150)),
        "long":   int(os.getenv("MAX_SUMMARY_LENGTH_LONG",   300)),
    }
    MIN_SUMMARY_LENGTH: int = int(os.getenv("MIN_SUMMARY_LENGTH", 30))

    # ── Critic Settings ────────────────────────────
    CRITIC_MAX_NEW_TOKENS: int = int(os.getenv("CRITIC_MAX_NEW_TOKENS", 200))
    CRITIC_TEMPERATURE: float = float(os.getenv("CRITIC_TEMPERATURE", 0.7))

    # ── Flask ──────────────────────────────────────
    FLASK_HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", 5000))
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")



config = Config()
