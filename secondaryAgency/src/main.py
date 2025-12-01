#!/usr/bin/python
# -*- coding: utf-8 -*-
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pathlib import Path
from contextlib import asynccontextmanager
from routers import index
from mqtt import mqttHandle
from sockets import inputNet, outputNet
from setting import settings


consciousnessSpacePath = Path(__file__).resolve().parent
logsPath = consciousnessSpacePath.parent / "logs/{time:YYYY-MM-DD}.log"

# 配置 Logger
logger.add(
    logsPath,
    rotation="1 day",
    level="INFO",
    enqueue=True,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)


async def startup():
    tasks = [mqttHandle.start()]
    if tasks:
        await asyncio.gather(*tasks)


async def shutdown():
    tasks = []
    mqttHandle.close()
    logger.complete()
    if tasks:
        await asyncio.gather(*tasks)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up... Initiating all dependent services")
    try:
        await startup()
        yield  # 应用运行中
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise e  # 启动失败应该抛出异常阻止应用运行
    finally:
        logger.info("Shutting down. Shutting down all dependent services.")
        await shutdown()
        logger.info("Bye!")


app = FastAPI(
    lifespan=lifespan,
    description="This docs",
)

# 加入跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 载入路由包
app.include_router(index.router)


# 404 错误处理
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    return JSONResponse({"message": "The interface does not exist."}, status_code=404)


if __name__ == "__main__":
    logger.debug(
        f"Service startup address: http://{settings.secondary_agency.host}:{settings.secondary_agency.port}"
    )
    try:
        uvicorn.run(
            "main:app",
            log_level=settings.secondary_agency.logLevel,
            reload=settings.secondary_agency.reload,
            workers=settings.secondary_agency.workers,
            host=settings.secondary_agency.host,
            port=settings.secondary_agency.port,
        )

    except KeyboardInterrupt:
        pass
