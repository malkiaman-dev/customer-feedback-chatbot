"""Simple weighted keyword retrieval over a predefined FAQ dataset."""
import json
import math
import re
from collections import Counter
from pathlib import Path

STOP_WORDS = set("a an the is are was were do does did i we you my your it its to of for and or in on at about what which how can please me need must should with from this that have tell explain include required requirements use using".split())
ALIASES = {"technologies": "technology", "tech": "technology", "stack": "technology", "deploying": "deploy", "deployment": "deploy", "deployed": "deploy", "hosting": "deploy", "submitting": "submit", "submission": "submit", "evaluated": "evaluation", "graded": "evaluation", "grading": "evaluation", "documents": "documentation", "errors": "error", "tools": "tool"}

def tokens(text):
    return {ALIASES.get(word, word) for word in re.findall(r"[a-z0-9]+", text.lower()) if word not in STOP_WORDS}

def load_faqs(path: Path):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, list) or not data:
        raise ValueError("The FAQ dataset must be a non-empty JSON list.")
    ids = set()
    for row in data:
        if not isinstance(row, dict) or any(not isinstance(row.get(key), str) or not row[key].strip() for key in ("id", "question", "answer")):
            raise ValueError("Each FAQ needs a non-empty id, question, and answer.")
        if row["id"] in ids:
            raise ValueError("FAQ identifiers must be unique.")
        ids.add(row["id"])
        keywords = row.get("keywords", [])
        if not isinstance(keywords, list) or not all(isinstance(word, str) for word in keywords):
            raise ValueError("FAQ keywords must be a list of strings.")
        if not isinstance(row.get("category", "General"), str):
            raise ValueError("FAQ categories must be strings.")
    return data

def retrieve(question, faqs, limit=3):
    query = tokens(question)
    if not query:
        return []
    documents = [tokens(row["question"] + " " + " ".join(row.get("keywords", []))) for row in faqs]
    frequency = Counter(word for document in documents for word in document)
    weights = {word: math.log(1 + len(faqs) / max(1, frequency[word])) for word in query}
    total_weight = sum(weights.values())
    ranked = []
    for row, document in zip(faqs, documents):
        overlap = query & document
        score = sum(weights[word] for word in overlap)
        if overlap and score / total_weight >= 0.6:
            ranked.append((score, row))
    ranked.sort(key=lambda item: item[0], reverse=True)
    if not ranked:
        return []
    # Keep close alternatives, rather than adding unrelated lower-ranked FAQs.
    best_score = ranked[0][0]
    return [row for score, row in ranked[:limit] if score >= best_score * 0.8]

def source_context(matches):
    return "\n\n".join(f"[{row['id']}]\nQuestion: {row['question']}\nAnswer: {row['answer']}" for row in matches)
