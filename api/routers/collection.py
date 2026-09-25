from fastapi import APIRouter

router = APIRouter(prefix="/collection", tags=["collection"])


@router.get("")
async def get_collection():
    return {"items": [], "total": 0}


@router.get("/{item_id}")
async def get_collection_item(item_id: int):
    return {"id": item_id, "name": "Exemple", "in_collection": True}
