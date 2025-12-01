from typing import Any, Dict, Literal, Optional
from fastapi import APIRouter, Body, Request
from loguru import logger
from pydantic import BaseModel
from fastapi.responses import ORJSONResponse
from mqtt import mqttHandle


router = APIRouter()

"""
将http协议转为其他协议
"""


@router.get("/")
async def hello():
    mqttHandle.subTopic("demo")
    return {"message": "http路由下2的测试2接口"}


@router.post("/")
async def hello(
    request: Request,
    data: Optional[Dict[str, Any]] = Body(
        None, description="任意格式的 JSON 数据（可选）"
    ),
):

    logger.info(f"测试webserver接收 {request.url}: {data}")
    return ORJSONResponse({"message": "测试接收", "data": data})
