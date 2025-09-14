from fastapi import APIRouter

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/")
async def list_tasks():
    return []
