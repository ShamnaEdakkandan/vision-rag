from pathlib import Path
import json

INDEX_FILE = Path("index/page_descriptions.json")

with open(
    INDEX_FILE,
    "r",
    encoding="utf-8"
) as f:
    page_descriptions = json.load(f)

query = input("Question: ").lower()

STOP_WORDS = {
    "what",
    "is",
    "are",
    "the",
    "a",
    "an",
    "for",
    "of",
    "to",
    "in",
    "on",
    "and",
    "or",
    "with"
}

best_page = None
best_score = 0

for page_path, description in page_descriptions.items():

    description = description.lower()

    score = 0

    for word in query.split():

        if word in STOP_WORDS:
            continue

        if word in description:
            score += 1

    if score > best_score:
        best_score = score
        best_page = page_path

print("\nBest Match:")
print(best_page)
print("Score:", best_score)