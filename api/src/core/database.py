import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dotenv import load_dotenv

from models.board import Board
from models.item import Item
from models.item_schema import ItemSchema

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "ai_board")

client = AsyncIOMotorClient(MONGODB_URI)
db = client[MONGODB_DB]

async def init_db():
    await init_beanie(
        database=db,
        document_models=[Board, Item, ItemSchema],
    )