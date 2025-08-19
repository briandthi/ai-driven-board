from fastapi import APIRouter, HTTPException, status, Body, Request
from typing import List
from models.item import Item
from beanie import PydanticObjectId

router = APIRouter(
    prefix="/items",
    tags=["items"]
)

@router.get("/by_board/{board_id}", response_model=List[Item])
async def get_items_by_board(board_id: str, request: Request):
    # Récupérer tous les filtres de la query string
    filters = []
    filters.append(Item.board_id == board_id)
    for key, value in request.query_params.items():
        if key == "board_id":
            continue  # déjà filtré
        if key.startswith("metadata."):
            meta_key = key.split(".", 1)[1]
            filters.append(Item.metadata[meta_key] == value)
        else:
            filters.append(getattr(Item, key) == value)
    # Combiner tous les filtres avec AND logique
    # Correction : Beanie accepte *filters pour un AND logique
    return await Item.find(*filters).to_list()

@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    await item.insert()
    return item

@router.get("/{id}", response_model=Item)
async def get_item(id: PydanticObjectId):
    item = await Item.get(id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/{id}", response_model=Item)
async def update_item(id: PydanticObjectId, item_data: Item):
    item = await Item.get(id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    update_data = item_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    await item.save()
    return item


@router.patch("/{id}", response_model=Item)
async def patch_item(id: PydanticObjectId, patch_data: dict = Body(...)):
    item = await Item.get(id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in patch_data.items():
        if field == "metadata" and isinstance(value, dict):
            # Fusionner intelligemment les metadata
            current_metadata = getattr(item, "metadata", {}) or {}
            updated_metadata = current_metadata.copy()
            updated_metadata.update(value)
            setattr(item, "metadata", updated_metadata)
        else:
            setattr(item, field, value)
    await item.save()
    return item

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(id: PydanticObjectId):
    item = await Item.get(id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await item.delete()
    return None
