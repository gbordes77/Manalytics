from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import json
from database.db_pool import get_db_connection
from src.api.models import ArchetypeResponse
from src.api.security import get_api_key

router = APIRouter()

@router.get("/", response_model=List[ArchetypeResponse])
async def get_all_archetypes(format: str):
    # TODO: Implement database query to fetch archetypes for a format
    return []

@router.put("/{archetype_id}/rules", dependencies=[Depends(get_api_key)])
async def update_archetype_rules(archetype_id: int, rules: List[Dict[str, Any]]):
    """
    Endpoint to update or add rules for an archetype. Requires API Key.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM archetype_rules WHERE archetype_id = %s;", (archetype_id,))
                for rule in rules:
                    cursor.execute(
                        "INSERT INTO archetype_rules (archetype_id, rule_type, rule_data) VALUES (%s, %s, %s);",
                        (archetype_id, rule['rule_type'], json.dumps(rule['rule_data']))
                    )
                conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    return {"status": "success", "message": f"Rules for archetype {archetype_id} updated."}