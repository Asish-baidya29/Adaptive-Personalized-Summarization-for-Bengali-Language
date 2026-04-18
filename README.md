# Adaptive Personalized Multilingual Summarizer

Personalized English summarization with Bengali output, powered by HuggingFace models and a critic-agent feedback loop.

---

## Project Structure

```
summarizer/
│
├── app.py                    # Flask entry point — routes only, no logic
├── config.py                 # Reads .env and exposes a Config object
├── .env                      # All secrets and settings (fill this in)
├── requirements.txt
│
├── agents/
│   ├── pipeline.py           # Orchestrates all 6 pipeline steps in order
│   └── critic_agent.py       # Critic LLM: reviews the initial summary
│
├── models/
│   ├── summarizer.py         # HuggingFace summarizer (first + second pass)
│   └── translator.py         # Your fine-tuned English → Bengali model
│
├── utils/
│   ├── preprocessor.py       # Cleans text, detects document type
│   └── user_profile.py       # User profile dataclass + prompt helpers
│
├── static/
│   ├── css/style.css         # All UI styles
│   └── js/main.js            # Frontend fetch + display logic
│
└── templates/
    └── index.html            # Single-page HTML template
```

---

## Setup

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Configure `.env`**

Open `.env` and fill in:
- `HUGGINGFACE_API_TOKEN` — your HuggingFace token (required for gated/private models)
- `BENGALI_MODEL` — your fine-tuned model ID on HuggingFace Hub, **or** set `BENGALI_MODEL_SOURCE=local` and `BENGALI_MODEL_LOCAL_PATH=./path/to/your/model`
- `SECRET_KEY` — change this to a random string before deploying

**3. Run the app**
```bash
python app.py
```

Then open `http://localhost:5000` in your browser.

---

## Pipeline (what happens when you click Summarize)

```
Input Text
    ↓
Preprocessing      → detects doc type (research paper / news / story / Q&A)
    ↓
User Profile       → knowledge level, style, length preference
    ↓
LLM Summarizer     → first-pass English summary (HuggingFace model)
    ↓
Critic Agent       → reviews summary vs. original text + user profile
    ↓
LLM Summarizer     → second-pass refined summary (uses critique)
    ↓
Bengali Translator → your fine-tuned model translates the refined summary
    ↓
Output             → shown to user with Bengali text
    ↓
User Feedback      → stored in session → critic becomes stricter/looser
```

---

## Using Your Fine-Tuned Bengali Model

If your model is saved locally:
```env
BENGALI_MODEL_SOURCE=local
BENGALI_MODEL_LOCAL_PATH=./models/your_finetuned_model
```

If it is uploaded to HuggingFace Hub:
```env
BENGALI_MODEL_SOURCE=hub
BENGALI_MODEL=your-username/your-model-name
```

---

## Extending to Other Indian Languages

1. Add the language to `LANGUAGES` list in `utils/user_profile.py`
2. Add a new translation pipeline in `models/translator.py` (or extend the existing one)
3. Add a language selector to the frontend form in `templates/index.html`
