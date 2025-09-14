from fastapi import APIRouter

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/")
async def list_customers():
    return []
