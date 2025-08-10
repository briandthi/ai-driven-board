from typing import Dict, Any

def generate_metadata_schema(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Génère dynamiquement le schéma à partir du contenu du champ metadata d'un item.
    Le schéma est un dict {clé: type}.
    """
    schema = {}
    for key, value in metadata.items():
        schema[key] = {
            "type": type(value).__name__,
            "required": value is not None
        }
    return schema

def deep_schema_diff(schema1: Dict[str, Any], schema2: Dict[str, Any]) -> bool:
    """
    Compare deux schémas de metadata (dict). Retourne True s'ils sont différents.
    """
    return schema1 != schema2