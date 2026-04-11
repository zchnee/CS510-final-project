import argparse
import json
import re
from pathlib import Path

from datasets import load_dataset


DEFAULT_DATASET = "kenantang/IdiomTranslate30"
DEFAULT_PETCI = Path("petci/json/filtered.json")
DEFAULT_OUTPUT = Path("data/chinese_english_idiom_examples.json")
DEFAULT_UNMATCHED = Path("data/unmatched_petci_idioms.json")


def normalize_zh(text):
    """Normalize Chinese idiom strings enough for dataset alignment."""
    text = re.sub(r"\s+", "", text or "")
    return (
        text.replace("\uFF0C", ",")
        .replace("\u3002", ".")
        .replace("\uFF1B", ";")
        .replace("\uFF1A", ":")
        .replace("\uFF1F", "?")
        .replace("\uFF01", "!")
        .replace("\u201C", '"')
        .replace("\u201D", '"')
        .replace("\u2018", "'")
        .replace("\u2019", "'")
    )


def load_petci(path):
    with path.open("r", encoding="utf-8") as f:
        rows = json.load(f)

    by_idiom = {}
    for row in rows:
        idiom = row["chinese"]
        key = normalize_zh(idiom)
        by_idiom[key] = {
            "petci_id": row["id"],
            "idiom_zh": idiom,
            "meaning_en": row["gold"],
            "alternative_meanings_en": row.get("human", []),
            "machine_meanings_en": row.get("machine", []),
        }
    return by_idiom


def english_translation_metadata(row):
    translations = {
        "creative": row.get("translate_creatively"),
        "analogy": row.get("translate_analogy"),
        "author": row.get("translate_author"),
    }
    translations = {k: v for k, v in translations.items() if v}
    sentence_en = (
        translations.get("author")
        or translations.get("creative")
        or translations.get("analogy")
    )
    return sentence_en, translations


def build_examples(
    petci_by_idiom,
    dataset_name,
    split,
    streaming,
    max_rows,
    max_pair_rows,
    progress_every,
):
    dataset = load_dataset(dataset_name, split=split, streaming=streaming)

    examples = []
    matched_petci_keys = set()
    stats = {
        "rows_scanned": 0,
        "chinese_english_rows": 0,
        "chinese_english_unmatched_rows": 0,
        "sample_unmatched_idioms": [],
    }
    for hf_idx, row in enumerate(dataset):
        if max_rows is not None and hf_idx >= max_rows:
            break

        stats["rows_scanned"] += 1
        if progress_every and stats["rows_scanned"] % progress_every == 0:
            print(
                "Scanned "
                f"{stats['rows_scanned']} rows; found "
                f"{stats['chinese_english_rows']} Chinese-English rows; matched "
                f"{len(examples)} examples"
            )

        if row.get("source_language") != "Chinese" or row.get("target_language") != "English":
            continue

        stats["chinese_english_rows"] += 1
        if max_pair_rows is not None and stats["chinese_english_rows"] > max_pair_rows:
            break

        key = normalize_zh(row.get("idiom"))
        petci = petci_by_idiom.get(key)
        if not petci:
            stats["chinese_english_unmatched_rows"] += 1
            if len(stats["sample_unmatched_idioms"]) < 20:
                stats["sample_unmatched_idioms"].append(row.get("idiom"))
            continue

        sentence_en, _ = english_translation_metadata(row)
        examples.append(
            {
                "idiom_zh": petci["idiom_zh"],
                "meaning_en": petci["meaning_en"],
                "alternative_meanings_en": petci["alternative_meanings_en"],
                "sentence_zh": row.get("sentence"),
                "sentence_en": sentence_en,
                "embedding_text_zh": row.get("sentence"),
                "petci_id": petci["petci_id"],
                "idiomtranslate30_index": hf_idx,
            }
        )
        matched_petci_keys.add(key)

    unmatched = [
        petci_by_idiom[key]
        for key in sorted(set(petci_by_idiom) - matched_petci_keys)
    ]
    return examples, unmatched, stats


def write_json(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    parser = argparse.ArgumentParser(
        description="Align PETCI Chinese idiom meanings with IdiomTranslate30 Chinese-English example sentences."
    )
    parser.add_argument("--petci", type=Path, default=DEFAULT_PETCI)
    parser.add_argument("--dataset", default=DEFAULT_DATASET)
    parser.add_argument("--split", default="train")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--unmatched-output", type=Path, default=DEFAULT_UNMATCHED)
    parser.add_argument("--max-rows", type=int, default=None)
    parser.add_argument("--max-pair-rows", type=int, default=None)
    parser.add_argument("--progress-every", type=int, default=50000)
    parser.add_argument("--no-streaming", action="store_true")
    args = parser.parse_args()

    petci_by_idiom = load_petci(args.petci)
    examples, unmatched, stats = build_examples(
        petci_by_idiom=petci_by_idiom,
        dataset_name=args.dataset,
        split=args.split,
        streaming=not args.no_streaming,
        max_rows=args.max_rows,
        max_pair_rows=args.max_pair_rows,
        progress_every=args.progress_every,
    )

    write_json(examples, args.output)
    write_json(unmatched, args.unmatched_output)

    print(f"Wrote {len(examples)} aligned examples to {args.output}")
    print(f"Wrote {len(unmatched)} unmatched PETCI idioms to {args.unmatched_output}")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    if examples:
        print(json.dumps(examples[0], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
