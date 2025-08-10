from typing import Optional, Dict, Any, List
from beanie import Document, Link
from pydantic import Field
from datetime import datetime, timezone

class ChecklistItem(Document):
    task: str
    completed: bool = False

class Item(Document):
    title: str
    type: str
    functional_description: Optional[str] = None
    technical_description: Optional[str] = None
    status: Optional[str] = "todo"
    checklist: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    board_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "items"
        indexes = [
            "board_id",
            "status"
        ]