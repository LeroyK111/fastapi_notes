from fastapi import APIRouter
from api import http, ws
from loguru import logger

# 子路由
router = APIRouter(
    prefix="/api/v1",
    tags=["api"],
    responses={
        500: {"description": "Internal Server Error"},
    },
)

# 需要的接口
router.include_router(http.router, prefix="/http", tags=["http"])
router.include_router(ws.router, prefix="/ws", tags=["ws"])
