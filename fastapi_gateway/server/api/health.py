import time

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def check_health():
    return {"status": 1, "time": time.time()}
