from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.boards import router as boards_router
from api.v1.items import router as items_router
from api.v1.schemas import router as schemas_router

import motor.motor_asyncio
from beanie import init_beanie
import os
from models.board import Board
from models.item import Item
from models.item_schema import ItemSchema

app = FastAPI()

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from utils.metadata_validator import MetadataValidator
from utils.item_schema_utils import generate_metadata_schema, deep_schema_diff

class MetadataValidationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Intercepter uniquement POST/PUT sur /items
        if request.method in ("POST", "PUT") and request.url.path.startswith("/items"):
            try:
                body = await request.json()
                # Validation simple
                if "metadata" in body:
                    body["metadata"] = MetadataValidator.validate(body["metadata"])
                    # --- Versionnement du schéma de metadata ---
                    item_type = body.get("type")
                    metadata = body.get("metadata", {})
                    if item_type and isinstance(metadata, dict):
                        # Générer le schéma courant
                        current_schema = generate_metadata_schema(metadata)
                        # Chercher la dernière version du schéma pour ce type
                        last_schema_doc = await ItemSchema.find(ItemSchema.item_type == item_type).sort("-version").first_or_none()
                        if last_schema_doc is None:
                            # Nouveau type : créer version 1
                            new_schema = ItemSchema(
                                item_type=item_type,
                                version=1,
                                schema=current_schema,
                                author="IA",  # ou récupérer l'utilisateur si dispo
                            )
                            await new_schema.insert()
                        else:
                            # Comparer avec le dernier schéma
                            if deep_schema_diff(current_schema, last_schema_doc.schema):
                                new_version = last_schema_doc.version + 1
                                new_schema = ItemSchema(
                                    item_type=item_type,
                                    version=new_version,
                                    schema=current_schema,
                                    author="IA",  # ou récupérer l'utilisateur si dispo
                                )
                                await new_schema.insert()
                    # Remplacer le body de la requête
                    request._body = JSONResponse(body).body
            except Exception:
                pass  # Si body non JSON ou autre, ne rien faire
        response = await call_next(request)
        return response

app.add_middleware(MetadataValidationMiddleware)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.on_event("startup")
async def app_init():
    # Connexion MongoDB
    mongo_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
    client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
    db_name = os.environ.get("MONGODB_DB", "ai_board")
    await init_beanie(
        database=client[db_name],
        document_models=[Board, Item, ItemSchema]
    )

app.include_router(boards_router)
app.include_router(items_router)
app.include_router(schemas_router)