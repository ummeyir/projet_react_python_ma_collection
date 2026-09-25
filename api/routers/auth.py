from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register_user():
    return {"message": "Inscription OK", "user": {"id": 1, "username": "demo"}}


@router.post("/login")
async def login_user():
    return {"message": "Connexion OK", "token": "fake-token"}
