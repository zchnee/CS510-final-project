"""
app.py - FastAPI Backend Server

Make sure you have pip installed fastapi, uvicorn before running the below cmd

Run with: python -m uvicorn app:app --reload
"""

import pickle
import os
import json
import subprocess
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from detect_idioms import detect_idioms

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ---------------------------------------------------------------------------
# Load idiom data once at startup
# ---------------------------------------------------------------------------

METADATA_PATH = "data/idioms_metadata.pkl"

idiom_set: set = set()
metadata_by_idiom: dict = {}

@app.on_event("startup")
def load_idiom_data():
    global idiom_set, metadata_by_idiom
    if not os.path.exists(METADATA_PATH):
        raise RuntimeError(
            f"Metadata not found at {METADATA_PATH}. Run build_index.py first."
        )
    with open(METADATA_PATH, "rb") as f:
        dataset = pickle.load(f)
    idiom_set = {entry["idiom_zh"] for entry in dataset}
    metadata_by_idiom = {entry["idiom_zh"]: entry for entry in dataset}
    print(f"[startup] Loaded {len(idiom_set)} idioms.")


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class DetectRequest(BaseModel):
    text: str


class TranslateRequest(BaseModel):
    text: str
    to: str = "en"
    source: str = "auto"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
TRANSLATE_SCRIPT_PATH = BASE_DIR / "frontend" / "scripts" / "translate.mjs"

@app.get("/")
def home():
    return { "message": "Server is up" }


@app.post("/detect")
def detect(req: DetectRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text must not be empty")

    matches = detect_idioms(req.text, idiom_set)

    enriched = []
    for match in matches:
        meta = metadata_by_idiom.get(match["idiom"], {})
        enriched.append({
            "idiom":                   match["idiom"],
            "start":                   match["start"],
            "end":                     match["end"],
            "meaning_en":              meta.get("meaning_en", ""),
            "alternative_meanings_en": meta.get("alternative_meanings_en", []),
            "sentence_zh":             meta.get("sentence_zh", ""),
            "sentence_en":             meta.get("sentence_en", ""),
        })

    return { "idioms": enriched }


@app.post("/translate")
def translate_text(req: TranslateRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text must not be empty")

    if not TRANSLATE_SCRIPT_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Translation script not found at {TRANSLATE_SCRIPT_PATH}",
        )

    payload = {
        "text": req.text,
        "to": req.to,
        "from": req.source,
    }

    try:
        result = subprocess.run(
            ["node", str(TRANSLATE_SCRIPT_PATH)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            timeout=20,
            check=True,
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Node.js was not found. Install Node.js and make sure `node` is on PATH.",
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Translation request timed out")
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=502,
            detail=e.stderr.strip() or "Translation provider failed",
        )

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="Invalid translation response")
