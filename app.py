import os
from flask import Flask, request, jsonify, render_template

# ── load .env ──────────────────────────────────────────────────────────────
def _load_env(path):
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except FileNotFoundError:
        pass

_load_env(os.path.join(os.path.dirname(__file__), ".env"))

from sarvamai import SarvamAI

api_key = os.environ.get("SARVAM_API_KEY")
if not api_key:
    raise RuntimeError("SARVAM_API_KEY not set in .env")

client = SarvamAI(api_subscription_key=api_key)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB

STT_MODEL = "saaras:v2"


def _normalise_upload(audio_file):
    """Standardise file metadata for Sarvam STT, which expects a WAV-compatible file."""
    filename = (audio_file.filename or "voice.wav").strip() or "voice.wav"
    content_type = (audio_file.content_type or audio_file.mimetype or "audio/wav").lower()

    if "webm" in filename.lower() or "webm" in content_type:
        content_type = "audio/wav"

    if not filename.lower().endswith((".wav", ".mp3", ".m4a", ".ogg")):
        name, ext = os.path.splitext(filename)
        filename = f"{name or 'voice'}.wav"

    return filename, content_type


# ── CPGRAMS system prompt ──────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert administrative assistant that converts raw citizen complaints into structured CPGRAMS (Centralised Public Grievance Redress and Monitoring System) grievances.

Given a citizen's complaint text, produce a structured grievance in the following exact JSON format:
{
  "subject": "<One-line summary, max 15 words>",
  "department": "<Most relevant ministry or department>",
  "category": "<Grievance category, e.g. Pension, Roads, Water Supply, Electricity, etc.>",
  "grievance_text": "<Formal, well-structured grievance in 3-5 sentences. Include: what the problem is, how long it has been occurring, what the citizen expects as resolution.>",
  "documents_required": ["<doc1>", "<doc2>"],
  "urgency": "High | Medium | Low"
}

Rules:
- Keep the tone formal and administrative.
- Infer the department from context (e.g. pension → Ministry of Finance / Department of Pension; roads → PWD / NHAI; electricity → Ministry of Power).
- documents_required should list 2-4 relevant supporting documents a citizen should attach.
- Output ONLY the JSON object — no extra text, no markdown fences.
"""

# ── routes ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/transcribe", methods=["POST"])
def transcribe():
    """Accept an audio file and return the transcript."""
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    audio_file = request.files["audio"]
    if audio_file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        audio_file.stream.seek(0)
        filename, content_type = _normalise_upload(audio_file)
        response = client.speech_to_text.transcribe(
            file=(filename, audio_file.stream, content_type),
            model=STT_MODEL,
            language_code="en-IN",
        )
        transcript = response.transcript if hasattr(response, "transcript") else str(response)
        return jsonify({"transcript": transcript})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/draft", methods=["POST"])
def draft():
    """Accept complaint text and return a structured CPGRAMS draft."""
    data = request.get_json(silent=True)
    if not data or not data.get("complaint"):
        return jsonify({"error": "No complaint text provided"}), 400

    complaint = data["complaint"].strip()
    if len(complaint) < 10:
        return jsonify({"error": "Complaint too short"}), 400

    try:
        response = client.chat.completions(
            model="sarvam-105b-conversations",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Complaint: {complaint}"},
            ],
        )
        raw = response.choices[0].message.content.strip()

        # Parse JSON from model response
        import json
        grievance = json.loads(raw)
        return jsonify({"grievance": grievance})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)

