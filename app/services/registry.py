from typing import Optional
from .faq_store import FaqStore
from .faq_search import FaqSearcher

store: Optional[FaqStore] = None
searcher: Optional[FaqSearcher] = None
