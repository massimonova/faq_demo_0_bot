from __future__ import annotations
from typing import List, Tuple
from rapidfuzz import process, fuzz
from .faq_store import FaqStore

class FaqSearcher:
    def __init__(self, store: FaqStore):
        self.store = store
        self._build()

    def _build(self):
        self.questions: List[str] = []
        self.keys: List[Tuple[str,int]] = []
        for cat in self.store.categories:
            for i, _ in enumerate(cat.items):
                self.questions.append(cat.items[i].q)
                self.keys.append((cat.id, i))

    def rebuild(self):
        self._build()

    def search(self, query: str, limit: int = 5, cutoff: int = 70) -> List[Tuple[str,int,str,int]]:
        # returns list of (cat_id, idx, question, score)
        results = process.extract(
            query,
            self.questions,
            scorer=fuzz.WRatio,
            limit=limit
        )
        out = []
        for q, score, pos in results:
            if score >= cutoff:
                cat_id, idx = self.keys[pos]
                out.append((cat_id, idx, q, score))
        return out
