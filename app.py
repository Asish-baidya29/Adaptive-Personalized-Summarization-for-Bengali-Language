import logging

from flask import Flask, render_template, request, jsonify, session

from config import config
from utils.user_profile import build_profile
from agents.pipeline import run_pipeline, apply_user_feedback

# ── Logging ────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Flask app ──────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# We keep the user profile in the Flask session so feedback persists
# across requests during the same browser session.
# For a production multi-user system, replace this with a database.


# ── Routes ─────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main single-page UI."""
    return render_template("index.html")


@app.route("/summarize", methods=["POST"])
def summarize():
    """
    Receive text + user profile, run the full pipeline, return results as JSON.

    Expected JSON body:
    {
      "text":            "...",
      "knowledge_level": "beginner" | "intermediate" | "expert" | "student" | "general",
      "summary_style":   "concise" | "detailed" | "bullet_points" | "narrative" | "technical",
      "summary_length":  "short" | "medium" | "long",
      "domain":          "science" | "law" | "general" | ...
    }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No JSON body received."}), 400

    raw_text = data.get("text", "").strip()
    if not raw_text:
        return jsonify({"error": "The 'text' field is required and cannot be empty."}), 400

    # Build user profile from form values
    profile = build_profile(
        knowledge_level = data.get("knowledge_level"),
        summary_style   = data.get("summary_style"),
        summary_length  = data.get("summary_length"),
        language        = "bengali",   # currently fixed; extend later
        domain          = data.get("domain"),
    )

    # Store profile in session so /feedback can update it
    session["profile"] = {
        "knowledge_level": profile.knowledge_level,
        "summary_style":   profile.summary_style,
        "summary_length":  profile.summary_length,
        "language":        profile.language,
        "domain":          profile.domain,
        "feedback_history": profile.feedback_history,
    }

    try:
        result = run_pipeline(raw_text=raw_text, user_profile=profile)
        return jsonify(result)
    except Exception as exc:
        logger.exception("Pipeline error")
        return jsonify({"error": str(exc)}), 500


@app.route("/feedback", methods=["POST"])
def feedback():
    """
    Receive a star rating + optional comment, store it in the session profile.
    The critic agent reads this history on the next /summarize call.

    Expected JSON body:
    {
      "rating":  1-5,
      "comment": "optional text"
    }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No JSON body received."}), 400

    rating = data.get("rating")
    comment = data.get("comment", "")

    if not isinstance(rating, int) or not (1 <= rating <= 5):
        return jsonify({"error": "rating must be an integer between 1 and 5."}), 400

    # Re-hydrate the profile from session
    session_data = session.get("profile", {})
    profile = build_profile(
        knowledge_level = session_data.get("knowledge_level"),
        summary_style   = session_data.get("summary_style"),
        summary_length  = session_data.get("summary_length"),
        domain          = session_data.get("domain"),
    )
    profile.feedback_history = session_data.get("feedback_history", [])

    apply_user_feedback(profile, rating=rating, comment=comment)

    # Save updated history back to session
    session["profile"]["feedback_history"] = profile.feedback_history

    return jsonify({"status": "ok", "message": "Feedback recorded."})


# ── Entry point ────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info(f"Starting server on {config.FLASK_HOST}:{config.FLASK_PORT}")
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG,
    )