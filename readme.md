# Output Schema

The aligned dataset in ``data/chinese_english_idiom_examples.json``.

Each entry has this structure:

```json
{
  "idiom_zh": "Chinese idiom",
  "meaning_en": "Primary English meaning from PETCI",
  "alternative_meanings_en": [
    "Alternative human-written English meaning"
  ],
  "sentence_zh": "Chinese example sentence from IdiomTranslate30",
  "sentence_en": "English translation(by LLM) as metadata from IdiomTranslate30",
  "embedding_text_zh": "Chinese text to embed for similarity search",
  "petci_id": "id in petci dataset",
  "idiomtranslate30_index": "index in idiomtranslate30 dataset"
}
```

`sentence_en` is included for display and comparison only.`embedding_text_zh` is for sentence embedding and FAISS retrieval step.
