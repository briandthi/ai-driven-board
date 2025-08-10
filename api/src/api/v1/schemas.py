from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from models.item_schema import ItemSchema

router = APIRouter(
    prefix="/schemas",
    tags=["schemas"]
)

@router.get("/", response_model=List[str])
async def list_item_types():
    """Liste tous les types d'item connus (distincts)."""
    types = await ItemSchema.distinct("item_type")
    return types

@router.get("/{item_type}", response_model=List[ItemSchema])
async def get_schemas_for_type(item_type: str):
    """Liste toutes les versions de schéma pour un type d'item."""
    schemas = await ItemSchema.find(ItemSchema.item_type == item_type).sort("-version").to_list()
    return schemas

@router.get("/{item_type}/latest", response_model=Optional[ItemSchema])
async def get_latest_schema(item_type: str):
    """Récupère le schéma courant (dernière version) pour un type d'item."""
    schema = await ItemSchema.find(ItemSchema.item_type == item_type).sort("-version").first_or_none()
    if not schema:
        raise HTTPException(status_code=404, detail="No schema found for this item type")
    return schema

@router.post("/", response_model=ItemSchema, status_code=status.HTTP_201_CREATED)
async def create_schema(schema: ItemSchema):
    """Crée une nouvelle version de schéma pour un type d'item."""
    await schema.insert()
    return schema