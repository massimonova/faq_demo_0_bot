from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import os, time, yaml

@dataclass
class FAQItem:
    q: str
    a: str
    media: Optional[str] = None
    aliases: List[str] = None
    buttons: List[Dict[str,str]] = None   # [{"text": "...", "url": "..."}]

@dataclass
class FAQCategory:
    id: str
    title: str
    items: List[FAQItem]


class FaqStore:
    def __init__(self, path: str):
        self.path = path
        self._mtime: float = 0.0
        self.categories: List[FAQCategory] = []
        self.popular_questions: List[str] = []
        self._q_index: Dict[Tuple[str,int], FAQItem] = {}
        self._q_to_key: Dict[str, Tuple[str,int]] = {}
        self.reload()

    def reload(self) -> None:
        if not os.path.exists(self.path):
            raise FileNotFoundError(self.path)
        with open(self.path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        cats, q_index, q_to_key = [], {}, {}

        for cat in data.get("categories", []):
            items = []
            for i, it in enumerate(cat.get("items", [])):
                item = FAQItem(
                    q=str(it.get("q", "")).strip(),
                    a=str(it.get("a", "")).strip(),
                    media=it.get("media"),
                    aliases=[str(x).strip() for x in it.get("aliases", [])],
                    buttons=[{"text":str(b.get("text", "")), "url":str(b.get("url", ""))}
                             for b in it.get("buttons", [])],
                )
                items.append(item)
                key = (cat["id"], i)
                q_index[key] = item
                q_to_key[item.q] = key
                for alias in item.aliases or []:
                    q_to_key.setdefault(alias, key)  # мапим алиасы на оригинал
            cats.append(FAQCategory(id=cat["id"], title=cat.get("title",""), items=items))

        self.categories = cats
        self.popular_questions = [str(x) for x in data.get("popular", [])]
        self._q_index, self._q_to_key = q_index, q_to_key
        self._mtime = os.path.getmtime(self.path)

    def reload_if_changed(self) -> bool:
        m = os.path.getmtime(self.path)
        if m != self._mtime:
            self.reload()
            return True
        return False

    def list_categories(self) -> List[FAQCategory]:
        return self.categories

    def get_category(self, cat_id: str) -> Optional[FAQCategory]:
        for c in self.categories:
            if c.id == cat_id:
                return c
        return None

    def get_item(self, cat_id: str, idx: int) -> Optional[FAQItem]:
        return self._q_index.get((cat_id, idx))

    def lookup_by_question(self, q: str) -> Optional[Tuple[str,int]]:
        return self._q_to_key.get(q)

    def popular(self) -> List[str]:
        return self.popular_questions

    def popular_titles(self) -> List[str]:
    # совместимость с хендлерами, которые ждут popular_titles()
        return self.popular()
