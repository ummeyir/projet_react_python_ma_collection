from fastapi import APIRouter, HTTPException

from seed import EXERCISES

router = APIRouter(prefix="/items", tags=["items"])


@router.get("")
async def list_items():
    return {"items": EXERCISES, "total": len(EXERCISES)}


@router.get("/{item_id}")
async def get_item(item_id: int):
    for exercise in EXERCISES:
        if exercise["id"] == item_id:
            return exercise

    raise HTTPException(status_code=404, detail=f"Exercice {item_id} introuvable")
