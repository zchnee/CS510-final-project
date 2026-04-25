"""
Build FAISS Index

Run this ONCE offline to generate:
  - data/idioms.index (FAISS vector index)
  - data/idioms_metadata.pkl (dataset entries for metadata retrieval)

Usage:
  python build_index.py
  python build_index.py --data data/chinese_english_idiom_examples.json --output data/
"""

import json
import pickle
import argparse
import os
import numpy as np

from sentence_transformers import SentenceTransformer
import faiss

MODEL_NAME  = "paraphrase-multilingual-MiniLM-L12-v2"
DATA_PATH   = "data/chinese_english_idiom_examples.json"
OUTPUT_DIR  = "data/"
INDEX_FILE  = "idioms.index"
METADATA_FILE = "idioms_metadata.pkl"
BATCH_SIZE  = 64

def load_dataset(path: str) -> list:
    """ Load the dataset and validate """

    print(f"[1/4] Loading dataset from {path}...")

    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found at: {path}")

    with open(path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    print(f"Loaded {len(dataset)} idiom entries.")

    required_fields = ["idiom_zh", "meaning_en", "embedding_text_zh"]
    for i, entry in enumerate(dataset):
        for field in required_fields:
            if field not in entry:
                raise ValueError(f"Entry {i} is missing required field: '{field}'")

    print(f"Validation passed — all entries have required fields.")
    return dataset


def generate_embeddings(dataset: list, model_name: str) -> np.ndarray:

    """
    Embed the embedding_text_zh field for each idiom entry.
    This is the Chinese example sentence prepared for similarity search.
    """
    print(f"\n[2/4] Loading sentence-transformer model: {model_name}")
    model = SentenceTransformer(model_name)

    texts = [entry["embedding_text_zh"] for entry in dataset]
    print(f"Embedding {len(texts)} sentences (batch size {BATCH_SIZE})...")

    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True
    )

    print(f"Embeddings shape: {embeddings.shape}")
    return embeddings


def build_faiss_index(embeddings: np.ndarray) -> faiss.Index:

    """
    Build a flat L2 FAISS index from the embedding matrix.
    IndexFlatL2 = exact nearest neighbor search, no approximation.
    Good for datasets up to ~100k entries.
    """

    print(f"\n[3/4] Building FAISS index...")

    dimension = embeddings.shape[1]
    print(f"Vector dimension: {dimension}")

    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype(np.float32)) # type: ignore

    print(f"Index built — {index.ntotal} vectors stored.")
    return index

def save_artifacts(index: faiss.Index, dataset: list, output_dir: str):

    """Save the FAISS index and dataset metadata to disk."""

    print(f"\n[4/4] Saving artifacts to {output_dir}...")

    os.makedirs(output_dir, exist_ok=True)

    index_path    = os.path.join(output_dir, INDEX_FILE)
    metadata_path = os.path.join(output_dir, METADATA_FILE)

    faiss.write_index(index, index_path)
    print(f"FAISS index saved at {index_path}")

    with open(metadata_path, "wb") as f:
        pickle.dump(dataset, f)
    print(f"Metadata saved at {metadata_path}")


# def run_quick_test(output_dir: str, model_name: str):

#     """
#      Sample test
#     """

#     index_path    = os.path.join(output_dir, INDEX_FILE)
#     metadata_path = os.path.join(output_dir, METADATA_FILE)

#     index = faiss.read_index(index_path)
#     with open(metadata_path, "rb") as f:
#         dataset = pickle.load(f)

#     model = SentenceTransformer(model_name)

#     # Test query — a Chinese sentence that should surface idioms about success/effort
#     test_query = "他们用威胁和利诱让我放弃了。"
#     print(f"Test query: \"{test_query}\"")

#     query_vector = model.encode([test_query]).astype(np.float32) # type: ignore
#     distances, indices = index.search(query_vector, k=3)

#     print(f"\nTop 3 matches:")
#     print(f"{'Rank':<6} {'Idiom':<15} {'Meaning':<40} {'Distance'}")
#     print(f"{'-'*75}")
#     for rank, (idx, dist) in enumerate(zip(indices[0],distances[0]), 1):
#         entry = dataset[idx]
#         print(f"{rank:<6} {entry['idiom_zh']:<15} {entry['meaning_en']:<40} {dist:.4f}")

def parse_args():
    parser = argparse.ArgumentParser(description="Build FAISS index")
    parser.add_argument("--data",default=DATA_PATH,help="Path to idioms.json")
    parser.add_argument("--output", default=OUTPUT_DIR, help="Output directory for index and metadata")
    parser.add_argument("--model",  default=MODEL_NAME, help="Sentence transformer model name")
    parser.add_argument("--skip-test", action="store_true", help="Skip the sanity check at the end")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    dataset = load_dataset(args.data)
    embeddings = generate_embeddings(dataset,args.model)
    index = build_faiss_index(embeddings)
    save_artifacts(index, dataset,args.output)

    # if not args.skip_test:
    #     run_quick_test(args.output, args.model)