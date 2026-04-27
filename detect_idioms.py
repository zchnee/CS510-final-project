"""
detect_idioms.py : Idiom Detection via Dictionary Lookup

Scans a Chinese sentence and returns all idiom spans found by matching substrings against the loaded idiom dataset.

"""

import pickle
import os

# This metadata will have the idioms from the dataset stored as a list which is easier to parse than reading the JSON again

METADATA_PATH = "data/idioms_metadata.pkl"


def load_idiom_set(metadata_path: str = METADATA_PATH) -> set:
    """
    Load all Chinese idioms from the metadata into a set for constant lookup

    Returns:
        A set of idiom strings
    """
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(
            f"Metadata not found at: {metadata_path}\n"
            f"Run build_index.py first to generate it."
        )

    with open(metadata_path,"rb") as f:
        dataset = pickle.load(f)

    idiom_set = {entry["idiom_zh"] for entry in dataset}
    return idiom_set

def detect_idioms(text: str, idiom_set: set) -> list:
    """
    Scan a Chinese sentence and return all idiom spans found using sliding window approach.

    Args:
        text: raw Chinese input string
        idiom_set: set of known idiom strings (from load_idiom_set)

    Returns:
        List of dicts, each with:
        {
            "idiom": the matched idiom string,
            "start": start index in original text,
            "end": end index in original text,
            "context": full surrounding sentence
        }
    """
    matches = []
    visited = set()

    # 15 char window is chosen as that is the max number of chars a chinese idiom has in our dataset, minimum is 3.

    max_window = min(len(text), 15)

    for start in range(len(text)):
        if start in visited:
            continue

        for window_size in range(max_window, 2, -1):
            end = start + window_size
            if end > len(text):
                continue

            span = text[start:end]

            if span in idiom_set:
                matches.append({
                    "idiom":   span,
                    "start":   start,
                    "end":     end,
                    "context": text
                })

                # mark these positions as visited to avoid double-matching
                for i in range(start, end):
                    visited.add(i)

                break

    return matches


if __name__ == "__main__":

    idiom_set = load_idiom_set()

    test_sentences = [
        "他们通过威逼利诱，想要我放弃诉讼。",
        "他真是马到成功，刚入职就升职了。",
        "这件事情让我半信半疑，不知道该怎么办。",
        "今天天气真好，我们去公园散步吧。"   # No Idioms are expected for this sentence
    ]

    for sentence in test_sentences:
        results = detect_idioms(sentence, idiom_set)
        print(f"\nInput: {sentence}")
        if results:
            for r in results:
                print(f"Found: [{r['idiom']}] at position {r['start']}–{r['end']}")
        else:
            print(f"No idioms detected.")