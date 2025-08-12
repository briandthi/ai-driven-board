import os
import logging
from typing import Dict
import httpx
from fastmcp import FastMCP

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s | %(levelname)s: %(message)s"
)
logger = logging.getLogger("mcp")

API_URL = os.environ.get("API_URL", "http://localhost:8000")

mcp = FastMCP(
    name="ai-driven-board-mcp",
    port=9000,
    host="0.0.0.0"
)

@mcp.tool()
async def create_item(
    title: str,
    type: str,
    functional_description: str = "",
    technical_description: str = "",
    board_id: str = "",
    status: str = "todo",
    checklist: list = [],
    metadata: Dict = {},
    first_request: bool = True
) -> Dict:
    """
    Create a new item in the board with dynamic metadata and optional board assignment.

    This tool allows you to create a new item (task, feature, bug, etc.) in the system,
    with flexible metadata and assignment to a board. It is typically used to add new
    tasks or requirements to a project board, with support for custom fields and checklists.

    Args:
        title (str): The title of the item. Required. Example: "Implement login page".
        type (str): The type/category of the item (e.g., "task", "bug", "feature"). Required.
        functional_description (str, optional): A user-facing description of the item's purpose or requirements. Default: "".
        technical_description (str, optional): Technical details or implementation notes. Default: "".
        board_id (str, optional): The ID of the board to assign the item to. If empty, the item is not assigned to a board. Default: "".
        status (str, optional): The status of the item (e.g., "todo", "in_progress", "done"). Default: "todo".
        checklist (list of dict, optional): A list of checklist items, each as a dict with keys "task" (str) and "completed" (bool). Default: [].
        metadata (dict, optional): Arbitrary key-value pairs for custom metadata (e.g., priority, tags, estimation, or anything else relevant for this item). Default: {}.
        first_request (bool, optional): Whether this is the first request for item creation. Default: True.

    Returns:
        dict: The created item as a dictionary, including its unique ID and all fields.

    Example:
        >>> create_item(
        ...     title="Add OAuth login",
        ...     type="feature",
        ...     functional_description="Allow users to log in with Google",
        ...     technical_description="Use OAuth2, update user model",
        ...     board_id="board123",
        ...     status="todo",
        ...     checklist=[{"task": "Design UI", "completed": False}],
        ...     metadata={"priority": "high"},
        ...     first_request=True
        ... )
        {
            "id": "item456",
            "title": "Add OAuth login",
            "type": "feature",
            "functional_description": "Allow users to log in with Google",
            "technical_description": "Use OAuth2, update user model",
            "board_id": "board123",
            "status": "todo",
            "checklist": [{"task": "Design UI", "completed": False}],
            "metadata": {"priority": "high"},
            "created_at": "...",
            "updated_at": "..."
        }

    Notes:
        - All fields not provided will use their default values.
        - The returned dictionary includes auto-generated fields such as "id", "created_at", and "updated_at".
        - Checklist items should be dictionaries with "task" (str) and "completed" (bool).
        
    Enhanced:
    - Checks if the type exists via the schemas API.
    - If type exists, compares requested metadata to the latest schema.
    - If metadata differ and first_request is True, returns a message explaining the differences and options.
    - If not first_request, creates the item regardless of differences.
    """
    payload = {
        "title": title,
        "type": type,
        "functional_description": functional_description,
        "technical_description": technical_description,
        "board_id": board_id,
        "status": status,
        "checklist": checklist,
        "metadata": metadata
    }
    logger.info(f"Enhanced create_item: check type/schema before POST {API_URL}/items")
    async with httpx.AsyncClient() as client:
        # 1. Vérifier si le type existe déjà via l'API schemas
        try:
            schema_resp = await client.get(f"{API_URL}/schemas/{type}/latest")
            if schema_resp.status_code == 404:
                # Type inconnu, on peut créer l'item normalement
                logger.info(f"Type {type} inconnu, création directe.")
            elif schema_resp.status_code == 200:
                schema = schema_resp.json()
                schema_metadata = schema.get("metadata", {})
                # 2. Comparer les metadata demandées à celles du modèle courant
                if metadata != schema_metadata:
                    if first_request:
                        # Générer un message d'explication structuré pour LLM
                        diff_keys = set(metadata.keys()) ^ set(schema_metadata.keys())
                        common_keys = set(metadata.keys()) & set(schema_metadata.keys())
                        value_diffs = {k: (metadata[k], schema_metadata[k]) for k in common_keys if metadata[k] != schema_metadata[k]}
                        explanation = {
                            "message": "Les metadata demandées diffèrent du modèle existant pour ce type.",
                            "diff_keys": list(diff_keys),
                            "value_diffs": value_diffs,
                            "conseil": (
                                "Vous pouvez soit utiliser le modèle existant (metadata actuelles), "
                                "soit proposer de nouveaux champs si vraiment nécessaires. "
                                "Si vous souhaitez forcer la création avec ces metadata, relancez la demande avec first_request=False."
                            ),
                            "metadata_attendu": schema_metadata,
                            "metadata_demande": metadata
                        }
                        logger.info(f"Différence de metadata détectée pour le type {type}: {explanation}")
                        return {"error": "metadata_mismatch", "explanation": explanation}
                    else:
                        logger.info(f"Différence de metadata ignorée (first_request=False), création forcée.")
                else:
                    logger.info(f"Metadata identiques au modèle existant, création normale.")
            else:
                logger.warning(f"Réponse inattendue de l'API schemas: {schema_resp.status_code} {schema_resp.text}")
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du schéma: {str(e)}")
            # On continue la création même si la vérification échoue

        # 3. Créer l'item normalement
        try:
            response = await client.post(f"{API_URL}/items/", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTPStatusError: {e.response.status_code} {e.response.text}")
            return {"error": f"API error: {e.response.status_code} {e.response.text}"}
        except Exception as e:
            logger.error(f"Exception lors de l'appel API: {str(e)}")
            return {"error": str(e)}

@mcp.tool()
async def update_item(
    id: str,
    title: str = "",
    type: str = "",
    functional_description: str = "",
    technical_description: str = "",
    board_id: str = "",
    status: str = "",
    checklist: list = [],
    metadata: Dict = {}
) -> Dict:
    """
    Update an existing item by ID with provided fields.
    Only non-empty fields will be updated.
    """
    payload = {}
    if title: payload["title"] = title
    if type: payload["type"] = type
    if functional_description: payload["functional_description"] = functional_description
    if technical_description: payload["technical_description"] = technical_description
    if board_id: payload["board_id"] = board_id
    if status: payload["status"] = status
    if checklist: payload["checklist"] = checklist
    if metadata: payload["metadata"] = metadata

    logger.info(f"PATCH {API_URL}/items/{id}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(f"{API_URL}/items/{id}", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTPStatusError: {e.response.status_code} {e.response.text}")
            return {"error": f"API error: {e.response.status_code} {e.response.text}"}
        except Exception as e:
            logger.error(f"Exception lors de l'appel API: {str(e)}")
            return {"error": str(e)}
        
@mcp.tool()
async def list_items(
    board_id: str
) -> Dict:
    """
    List all items for a given board.
    """
    logger.info(f"GET {API_URL}/items/by_board/{board_id}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_URL}/items/by_board/{board_id}")
            response.raise_for_status()
            return {"items": response.json()}
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTPStatusError: {e.response.status_code} {e.response.text}")
            return {"error": f"API error: {e.response.status_code} {e.response.text}"}
        except Exception as e:
            logger.error(f"Exception lors de l'appel API: {str(e)}")
            return {"error": str(e)}


@mcp.tool()
async def create_board(
    name: str,
    description: str = "",
    color: str = "",
    metadata: Dict = None
) -> Dict:
    """
    Create a new board with the given parameters.
    """
    payload = {
        "name": name,
        "description": description,
        "color": color,
        "metadata": metadata if metadata is not None else {}
    }
    logger.info(f"POST {API_URL}/boards/")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{API_URL}/boards/", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTPStatusError: {e.response.status_code} {e.response.text}")
            return {"error": f"API error: {e.response.status_code} {e.response.text}"}
        except Exception as e:
            logger.error(f"Exception lors de l'appel API: {str(e)}")
            return {"error": str(e)}



@mcp.tool()
async def find_related_items(
    board_id: str,
    query: str = ""
) -> Dict:
    """
    Find items in a board related to a query (searches title and descriptions).
    """
    logger.info(f"GET {API_URL}/items/by_board/{board_id} for related items")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_URL}/items/by_board/{board_id}")
            response.raise_for_status()
            items = response.json()
            if query:
                q = query.lower()
                filtered = [
                    item for item in items
                    if q in (item.get("title", "").lower() + " " +
                             item.get("functional_description", "").lower() + " " +
                             item.get("technical_description", "").lower())
                ]
                return {"items": filtered}
            return {"items": items}
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTPStatusError: {e.response.status_code} {e.response.text}")
            return {"error": f"API error: {e.response.status_code} {e.response.text}"}
        except Exception as e:
            logger.error(f"Exception lors de l'appel API: {str(e)}")
            return {"error": str(e)}

@mcp.tool()
async def delete_item(
    id: str
) -> Dict:
    """
    Supprime un item du board via son identifiant.

    Ce tool MCP effectue un appel HTTP DELETE sur l'endpoint /items/{id} de l'API REST.
    Il retourne le résultat de la suppression ou un message d'erreur structuré.

    Args:
        id (str): Identifiant unique de l'item à supprimer.

    Returns:
        dict: Résultat de la suppression ou message d'erreur.

    Exemple:
        >>> delete_item(id="item123")
        {"success": true, "message": "Item supprimé"}
    """
    logger.info(f"DELETE {API_URL}/items/{id}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(f"{API_URL}/items/{id}")
            response.raise_for_status()
            try:
                data = response.json()
            except Exception:
                data = response.text if response.text else None
            return {"success": True, "message": "Item supprimé", "data": data}
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTPStatusError: {e.response.status_code} {e.response.text}")
            return {"success": False, "error": f"API error: {e.response.status_code} {e.response.text}"}
        except Exception as e:
            logger.error(f"Exception lors de l'appel API: {str(e)}")
            return {"success": False, "error": str(e)}
if __name__ == "__main__":
    # Utilisation du transport HTTP streamable (POST/GET/SSE) recommandé pour reverse proxy
    mcp.run(transport='streamable-http')