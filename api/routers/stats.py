from fastapi import APIRouter

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("")
async def get_stats():
    return {"total_items": 0, "total_collection": 0, "favorite_count": 0}
