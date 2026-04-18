"use strict";

let selectedRating = 0;   // tracks which star the user clicked

// ── Main pipeline call ─────────────────────────────────────────────

async function runPipeline() {
  const inputText = document.getElementById("inputText").value.trim();

  if (!inputText) {
    showError("Please paste some English text before submitting.");
    return;
  }

  // Gather user profile values
  const payload = {
    text:            inputText,
    knowledge_level: document.getElementById("knowledgeLevel").value,
    summary_style:   document.getElementById("summaryStyle").value,
    summary_length:  document.getElementById("summaryLength").value,
    domain:          document.getElementById("domain").value.trim() || "general",
  };

  hideError();
  showLoader(true);
  hideResults();

  try {
    const response = await fetch("/summarize", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "An unknown error occurred.");
    }

    displayResults(data);

  } catch (err) {
    showError("Pipeline error: " + err.message);
  } finally {
    showLoader(false);
  }
}


// ── Display results ────────────────────────────────────────────────

function displayResults(data) {
  // Meta tags
  const metaBar = document.getElementById("metaBar");
  metaBar.innerHTML = [
    `<span class="meta-tag">📄 ${data.doc_type}</span>`,
    `<span class="meta-tag">${data.word_count} words</span>`,
    `<span class="meta-tag">${data.estimated_reading_time}</span>`,
  ].join("");

  document.getElementById("timingTag").textContent = `⏱ ${data.elapsed_seconds}s`;

  // Pipeline outputs
  document.getElementById("initialSummary").textContent  = data.initial_summary;
  document.getElementById("critique").textContent        = data.critique;
  document.getElementById("refinedSummary").textContent  = data.refined_summary;
  document.getElementById("bengaliOutput").textContent   = data.bengali_output;

  // Reset feedback UI
  selectedRating = 0;
  updateStars(0);
  document.getElementById("feedbackComment").value = "";
  document.getElementById("feedbackMsg").textContent    = "";

  // Show results card
  document.getElementById("results").classList.add("visible");
  document.getElementById("results").scrollIntoView({ behavior: "smooth" });
}


// ── Feedback ───────────────────────────────────────────────────────

function selectRating(rating) {
  selectedRating = rating;
  updateStars(rating);
}

function updateStars(rating) {
  document.querySelectorAll(".star-btn").forEach((btn) => {
    const btnRating = parseInt(btn.dataset.rating, 10);
    btn.classList.toggle("active", btnRating <= rating);
  });
}

async function submitFeedback() {
  if (selectedRating === 0) {
    document.getElementById("feedbackMsg").textContent = "Please select a star rating first.";
    document.getElementById("feedbackMsg").style.color = "#d97706";
    return;
  }

  const comment = document.getElementById("feedbackComment").value.trim();
  const payload = { rating: selectedRating, comment };

  try {
    const response = await fetch("/feedback", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) throw new Error(data.error || "Feedback submission failed.");

    document.getElementById("feedbackMsg").textContent = "✓ Thank you! Your feedback will improve future summaries.";
    document.getElementById("feedbackMsg").style.color = "#2f9e44";

  } catch (err) {
    document.getElementById("feedbackMsg").textContent = "Could not submit feedback: " + err.message;
    document.getElementById("feedbackMsg").style.color = "#a8071a";
  }
}


// ── UI helpers ─────────────────────────────────────────────────────

function showLoader(visible) {
  document.getElementById("loader").classList.toggle("visible", visible);
}

function hideResults() {
  document.getElementById("results").classList.remove("visible");
}

function showError(message) {
  const banner = document.getElementById("errorBanner");
  banner.textContent = message;
  banner.classList.add("visible");
  banner.scrollIntoView({ behavior: "smooth" });
}

function hideError() {
  document.getElementById("errorBanner").classList.remove("visible");
}