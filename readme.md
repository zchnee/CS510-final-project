# CS510 Final Project — Idiom-Aware Chinese–English Translator

A full-stack Chinese-to-English translation app with an idiom-aware explanation layer for Chinese idiomatic expressions (成语). The system translates user input, detects idioms in the original Chinese text, and presents enriched metadata such as English meanings, alternative translations, and example sentence pairs. The backend combines FastAPI, dictionary-based idiom span detection, FAISS-backed metadata generation, and a Node bridge to `@vitalets/google-translate-api`; the frontend provides an interactive React interface for translation output, highlighted idioms, and explanation cards.

---

## Project Structure

```
CS510-final-project/
├── app.py                  # FastAPI backend server
├── build_index.py          # One-time FAISS index builder
├── detect_idioms.py        # Sliding-window idiom detection
├── get_data.py             # Dataset alignment script (PETCI + IdiomTranslate30)
├── requirements.txt        # Python dependencies
├── data/
│   ├── chinese_english_idiom_examples.json  # Aligned idiom dataset
│   ├── idioms.index                         # FAISS index (generated)
│   └── idioms_metadata.pkl                  # Metadata pickle (generated)
└── frontend/               # React + TypeScript frontend (Vite)
    └── scripts/
        └── translate.mjs    # Node bridge for Google Translate API
```

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- pip packages: installed from `requirements.txt`
- npm packages: installed from `frontend/package.json`, including `@vitalets/google-translate-api`

---

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Build the FAISS index

This only needs to be run **once**. It downloads the sentence-transformer model (~120 MB on first run) and generates `data/idioms.index` and `data/idioms_metadata.pkl`.

```bash
python build_index.py
```

### 3. Start the backend

```bash
python -m uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`.

### 4. Install and start the frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

> The frontend proxies `/api/*` requests to the backend at `http://localhost:8000`, so both must be running at the same time.

You can test the translation bridge directly:

```bash
echo '{"text":"你好，世界","to":"en"}' | node frontend/scripts/translate.mjs
```

---

## API

### `POST /detect`

Detects Chinese idioms in input text and returns enriched metadata for each match.

**Request body:**
```json
{ "text": "他真是马到成功，刚入职就升职了。" }
```

**Response:**
```json
{
  "idioms": [
    {
      "idiom": "马到成功",
      "start": 3,
      "end": 7,
      "meaning_en": "immediate success",
      "alternative_meanings_en": ["win instant success", "succeed at once"],
      "sentence_zh": "他真是马到成功，刚入职就升职了。",
      "sentence_en": "He truly achieved immediate success, getting promoted right after joining."
    }
  ]
}
```

### `POST /translate`

Translates Chinese text to English using `@vitalets/google-translate-api` through the Node bridge at `frontend/scripts/translate.mjs`.

**Request body:**
```json
{ "text": "你好，世界", "to": "en" }
```

**Response:**
```json
{
  "text": "Hello world"
}
```

---

## Dataset Schema

The aligned dataset is at `data/chinese_english_idiom_examples.json`. Each entry has this structure:

```json
{
  "idiom_zh": "Chinese idiom",
  "meaning_en": "Primary English meaning from PETCI",
  "alternative_meanings_en": [
    "Alternative human-written English meaning"
  ],
  "sentence_zh": "Chinese example sentence from IdiomTranslate30",
  "sentence_en": "English translation (by LLM) as metadata from IdiomTranslate30",
  "embedding_text_zh": "Chinese text to embed for similarity search",
  "petci_id": "id in petci dataset",
  "idiomtranslate30_index": "index in idiomtranslate30 dataset"
}
```

`sentence_en` is included for display and comparison only. `embedding_text_zh` is used for sentence embedding and FAISS retrieval.

---

## Team

| Name | NetID | Role |
|---|---|---|
| Larry Liao | larryl3 | Frontend (React) |
| Yixin Zhou | yixinz10 | Dataset, idiom extraction |
| Abuzar Hussain Mohammad | ahm7 | FAISS index, backend server |
| Andrew Chen | andrew45 | Evaluation methodology |

Project Coordinator: Andrew Chen (andrew45)
