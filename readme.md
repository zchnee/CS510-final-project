# CS510 Final Project — Chinese–English Idiom-Aware Translation System

A web app for Chinese–English translation with a specialized focus on idiomatic expressions (成语). It detects Chinese idioms in input text and returns their English meanings, alternative translations, and example sentences using FAISS-based semantic retrieval.

---

## Project Structure

```
CS510-final-project/
├── app.py                  # FastAPI backend server
├── build_index.py          # One-time FAISS index builder
├── detect_idioms.py        # Sliding-window idiom detection
├── get_data.py             # Dataset alignment script (PETCI + IdiomTranslate30)
├── data/
│   ├── chinese_english_idiom_examples.json  # Aligned idiom dataset
│   ├── idioms.index                         # FAISS index (generated)
│   └── idioms_metadata.pkl                  # Metadata pickle (generated)
└── frontend/               # React + TypeScript frontend (Vite)
```

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- pip packages: `fastapi`, `uvicorn`, `sentence-transformers`, `faiss-cpu`, `datasets`

---

## Setup

### 1. Install Python dependencies

```bash
pip install fastapi uvicorn sentence-transformers faiss-cpu datasets
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
| Andrew Chen | andrew45 | Translation API integration |

Project Coordinator: Andrew Chen (andrew45)

