# Grievance Drafter — Powered by Sarvam AI

Convert unstructured citizen voice complaints into well-structured **CPGRAMS** administrative grievances using [Sarvam AI](https://sarvam.ai).

---

## What it does

1. **Voice / text input** — Record a complaint in the browser or type/paste it
2. **Auto-transcription** — Voice converted to text via Sarvam's **Saaras v2** STT model
3. **CPGRAMS draft** — Raw complaint structured into a formal grievance by **sarvam-105b-conversations**, with:
   - Subject line
   - Responsible Ministry / Department
   - Grievance category
   - Urgency level
   - Formal grievance text
   - List of supporting documents to attach
4. **Copy to clipboard** — One click to copy the full draft

---

## Tech stack

| Layer | Technology |
|---|---|
| AI models | Sarvam AI (`saaras:v2` STT + `sarvam-105b-conversations`) |
| Backend | Python / Flask |
| Frontend | Vanilla HTML + CSS + JS (no framework) |
| SDK | `sarvamai` (official Python SDK) |

---

## Quick start

```bash
# 1. Clone
git clone https://github.com/Ishwari-create/sarvam-Grievance-Drafter.git
cd sarvam-Grievance-Drafter

# 2. Install dependencies
pip install sarvamai flask

# 3. Add your Sarvam API key
cp .env.example .env
# Edit .env and paste your key: SARVAM_API_KEY=sk_...

# 4. Run
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## Project structure

```
├── app.py              ← Flask backend (/, /transcribe, /draft)
├── templates/
│   └── index.html      ← Single-page UI
├── static/
│   └── style.css       ← Styling
├── sarvam_chat.py      ← Minimal API smoke-test script
├── .env.example        ← Environment variable template
└── .gitignore
```

---

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Web UI |
| `POST` | `/transcribe` | Upload audio file → returns `{ transcript }` |
| `POST` | `/draft` | Send `{ complaint }` text → returns structured CPGRAMS grievance JSON |

---

## Getting a Sarvam API key

Sign up at [sarvam.ai](https://sarvam.ai) → Dashboard → API Keys.

