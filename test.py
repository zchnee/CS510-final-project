# This is to test the max,min, most commonly used idiom length

import json

with open("data/chinese_english_idiom_examples.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

lengths = [len(entry["idiom_zh"]) for entry in dataset]
print(f"Min: {min(lengths)}")
print(f"Max: {max(lengths)}")
print(f"Most common: {max(set(lengths), key=lengths.count)}")