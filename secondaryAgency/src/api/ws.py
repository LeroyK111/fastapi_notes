from fastapi import APIRouter
from loguru import logger


router = APIRouter()

"""
将websocket协议转为其他协议
"""


@router.get("/1")
async def hello():
    return {"message": "ws/1"}
