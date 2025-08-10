from typing import Optional, Dict, Any
from beanie import Document
from pydantic import Field
from datetime import datetime, timezone

class Board(Document):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory= datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory= datetime.now(timezone.utc))

    class Settings:
        name = "boards"