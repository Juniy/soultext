from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class NovelStatus(str, Enum):
    IDEA = "idea"
    OUTLINING = "outlining"
    WRITING = "writing"
    REVISING = "revising"
    COMPLETED = "completed"


class Character(BaseModel):
    id: str = Field(default="", description="唯一标识")
    name: str = Field(description="角色名称")
    nicknames: List[str] = Field(default_factory=list)
    gender: Optional[str] = None
    age: Optional[str] = None
    personality: List[str] = Field(default_factory=list)
    background: str = Field(default="")
    appearance: str = Field(default="")
    motivation: str = Field(default="")
    arc: List[str] = Field(default_factory=list)
    relationships: Dict[str, str] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    notes: str = Field(default="")


class Location(BaseModel):
    id: str = Field(default="")
    name: str = Field(description="地点名称")
    type: str = Field(default="")
    description: str = Field(default="")
    significance: str = Field(default="")
    history: str = Field(default="")
    related_locations: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class Scene(BaseModel):
    id: str = Field(default="")
    title: str = Field(description="场景标题")
    chapter_id: Optional[str] = None
    location_id: Optional[str] = None
    characters: List[str] = Field(default_factory=list)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    summary: str = Field(default="")
    content: str = Field(default="")
    mood: str = Field(default="")
    plot_function: str = Field(default="")
    word_count: int = Field(default=0)


class Timeline(BaseModel):
    id: str = Field(default="")
    novel_id: str = Field(default="")
    title: str = Field(default="")
    events: List[Dict[str, Any]] = Field(default_factory=list)
    eras: List[Dict[str, Any]] = Field(default_factory=list)


class Chapter(BaseModel):
    id: str = Field(default="")
    novel_id: str = Field(default="")
    number: int = Field(default=0)
    title: str = Field(default="")
    summary: str = Field(default="")
    content: str = Field(default="")
    word_count: int = Field(default=0)
    status: str = Field(default="draft")
    scenes: List[str] = Field(default_factory=list)
    pov_character: Optional[str] = None
    notes: str = Field(default="")


class WorldBuilding(BaseModel):
    id: str = Field(default="")
    novel_id: str = Field(default="")
    category: str = Field(default="")
    name: str = Field(default="")
    description: str = Field(default="")
    rules: List[str] = Field(default_factory=list)
    related_entities: List[str] = Field(default_factory=list)


class Novel(BaseModel):
    id: str = Field(default="")
    title: str = Field(default="新作品")
    author: str = Field(default="")
    genre: str = Field(default="")
    status: NovelStatus = Field(default=NovelStatus.IDEA)
    description: str = Field(default="一句话灵感")
    word_count_target: int = Field(default=5000000)
    word_count_current: int = Field(default=0)
    chapters: List[Chapter] = Field(default_factory=list)
    characters: Dict[str, Character] = Field(default_factory=dict)
    locations: Dict[str, Location] = Field(default_factory=dict)
    scenes: Dict[str, Scene] = Field(default_factory=dict)
    timeline: Optional[Timeline] = None
    world_building: Dict[str, WorldBuilding] = Field(default_factory=dict)
    outline: str = Field(default="")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def get_progress(self) -> float:
        if self.word_count_target <= 0:
            return 0.0
        return min(100.0, (self.word_count_current / self.word_count_target) * 100.0)
