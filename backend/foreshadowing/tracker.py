"""??/??????"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime

class ClueStatus(str, Enum):
    PLANTED = "planted"
    ACTIVE = "active"
    FULFILLED = "fulfilled"
    ABANDONED = "abandoned"

@dataclass
class ForeshadowClue:
    id: str
    novel_id: str
    description: str
    clue_type: str = "general"
    importance: int = 1
    planted_chapter: int = 0
    expected_recall_chapter: int = 0
    actual_recall_chapter: int = 0
    status: ClueStatus = ClueStatus.PLANTED
    related_entities: list = field(default_factory=list)
    keywords: list = field(default_factory=list)
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

class ForeshadowingTracker:
    def __init__(self):
        self._clues: Dict[str, ForeshadowClue] = {}

    def add_clue(self, clue):
        self._clues[clue.id] = clue
        return clue

    def get_clue(self, clue_id):
        return self._clues.get(clue_id)

    def update_clue(self, clue_id, **kwargs):
        clue = self._clues.get(clue_id)
        if not clue: return None
        for k, v in kwargs.items():
            if hasattr(clue, k): setattr(clue, k, v)
        clue.updated_at = datetime.now().isoformat()
        return clue

    def fulfill_clue(self, clue_id, chapter):
        clue = self._clues.get(clue_id)
        if not clue: return None
        clue.status = ClueStatus.FULFILLED
        clue.actual_recall_chapter = chapter
        clue.updated_at = datetime.now().isoformat()
        return clue

    def get_novel_clues(self, novel_id):
        return [c for c in self._clues.values() if c.novel_id == novel_id]

    def get_active_clues(self, novel_id):
        return [c for c in self._clues.values() if c.novel_id == novel_id and c.status in (ClueStatus.PLANTED, ClueStatus.ACTIVE)]

    def get_overdue_clues(self, novel_id, current_chapter):
        return [c for c in self._clues.values()
                if c.novel_id == novel_id and c.status in (ClueStatus.PLANTED, ClueStatus.ACTIVE)
                and c.expected_recall_chapter > 0 and current_chapter > c.expected_recall_chapter + 5]

    def delete_clue(self, clue_id):
        if clue_id in self._clues:
            del self._clues[clue_id]
            return True
        return False

    def get_all_clues(self):
        return list(self._clues.values())

    def to_dict(self):
        return {k: self._serialize_clue(c) for k, c in self._clues.items()}

    def _serialize_clue(self, c):
        return {"id": c.id, "novel_id": c.novel_id, "description": c.description, "clue_type": c.clue_type,
                "importance": c.importance, "planted_chapter": c.planted_chapter, "expected_recall_chapter": c.expected_recall_chapter,
                "actual_recall_chapter": c.actual_recall_chapter, "status": c.status.value, "related_entities": c.related_entities,
                "keywords": c.keywords, "notes": c.notes, "created_at": c.created_at, "updated_at": c.updated_at}

    def from_dict(self, data):
        for k, v in data.items():
            c = ForeshadowClue(id=v["id"], novel_id=v["novel_id"], description=v["description"], clue_type=v.get("clue_type", "general"),
                               importance=v.get("importance", 1), planted_chapter=v.get("planted_chapter", 0),
                               expected_recall_chapter=v.get("expected_recall_chapter", 0), actual_recall_chapter=v.get("actual_recall_chapter", 0),
                               status=ClueStatus(v.get("status", "planted")), related_entities=v.get("related_entities", []),
                               keywords=v.get("keywords", []), notes=v.get("notes", ""),
                               created_at=v.get("created_at", ""), updated_at=v.get("updated_at", ""))
            self._clues[k] = c

    def get_statistics(self):
        total = len(self._clues)
        planted = sum(1 for c in self._clues.values() if c.status == ClueStatus.PLANTED)
        fulfilled = sum(1 for c in self._clues.values() if c.status == ClueStatus.FULFILLED)
        return {"total_clues": total, "planted": planted, "fulfilled": fulfilled,
                "fulfillment_rate": round(fulfilled / total * 100, 1) if total > 0 else 0}
