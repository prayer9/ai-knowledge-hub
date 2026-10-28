from datetime import datetime, timezone
from itertools import count
from threading import Lock
from app.models import KnowledgeBase, KnowledgeBaseInput

class Store:
    def __init__(self):
        self.items: dict[int, KnowledgeBase] = {}
        self.ids = count(1)
        self.lock = Lock()

    def create(self, data: KnowledgeBaseInput) -> KnowledgeBase:
        with self.lock:
            item = KnowledgeBase(id=next(self.ids), created_at=datetime.now(timezone.utc), **data.model_dump())
            self.items[item.id] = item
            return item

    def list(self) -> list[KnowledgeBase]:
        with self.lock:
            return list(self.items.values())

    def get(self, item_id: int) -> KnowledgeBase | None:
        with self.lock:
            return self.items.get(item_id)

    def update(self, item_id: int, data: KnowledgeBaseInput) -> KnowledgeBase | None:
        with self.lock:
            item = self.items.get(item_id)
            if item is None:
                return None
            item = item.model_copy(update=data.model_dump())
            self.items[item_id] = item
            return item

    def delete(self, item_id: int) -> bool:
        with self.lock:
            return self.items.pop(item_id, None) is not None
