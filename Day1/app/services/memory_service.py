from typing import List
from app.schemas.memory import MemoryItem, MemoryHistory


class MemoryService:
    def __init__(self) -> None:
        self._history = MemoryHistory()

    def add_entry(self, skills: str, interests: str, goal: str) -> MemoryItem:
        item = MemoryItem(skills=skills, interests=interests, goal=goal)
        self._history.items.append(item)
        return item

    def get_all_entries(self) -> List[MemoryItem]:
        return self._history.items

    def clear(self) -> None:
        self._history.items.clear()


memory_service = MemoryService()
