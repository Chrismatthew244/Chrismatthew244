from fastapi import APIRouter

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/")
async def list_billing():
    return []
