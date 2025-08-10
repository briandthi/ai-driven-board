from typing import Optional, Dict, Any
from beanie import Document
from pydantic import Field
from datetime import datetime, timezone

class ItemSchema(Document):
    item_type: str  # type d'item (ex: "feature", "bug", etc.)
    version: int = 1  # version du schéma (auto-incrément ou géré par l'IA)
    schema: Dict[str, Any] = Field(default_factory=dict)  # schéma JSON
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    author: Optional[str] = None  # "IA" ou nom utilisateur

    class Settings:
        name = "item_schemas"
        indexes = [
            [("item_type", 1), ("version", -1)]  # index composé pour recherche rapide
        ]