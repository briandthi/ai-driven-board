from fastapi import APIRouter, HTTPException, status
from typing import List
from models.board import Board
from beanie import PydanticObjectId

router = APIRouter(
    prefix="/boards",
    tags=["boards"]
)

@router.get("/", response_model=List[Board])
async def list_boards():
    return await Board.find_all().to_list()

@router.post("/", response_model=Board, status_code=status.HTTP_201_CREATED)
async def create_board(board: Board):
    await board.insert()
    return board

@router.get("/{id}", response_model=Board)
async def get_board(id: PydanticObjectId):
    board = await Board.get(id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board

@router.put("/{id}", response_model=Board)
async def update_board(id: PydanticObjectId, board_data: Board):
    board = await Board.get(id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    update_data = board_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(board, field, value)
    await board.save()
    return board

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(id: PydanticObjectId):
    board = await Board.get(id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    await board.delete()
    return None