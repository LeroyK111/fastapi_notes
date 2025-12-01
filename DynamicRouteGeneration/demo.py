#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
add_route 和 add_api_route 用于动态添加路由，但 add_api_route 提供了更多与 FastAPI 集成的特性。
include_router 是为了模块化和结构化大型应用。
app.mount() 用于挂载子应用或其他服务（如静态文件服务）。
@app.websocket_route() 可以动态添加 WebSocket 路由。
app.add_middleware() 和中间件可以用于在路由之前或之后执行逻辑。
子应用动态生成 适合模块化和动态加载部分功能。
自定义路由处理器 提供了高度灵活性，适合复杂的自定义需求。
"""

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


# 加入跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 假设从配置文件或数据库中获取到路径列表
dynamic_paths = ["/route1", "/route2", "/route3"]


# 路由装饰器
@app.get("/")
def read_root():
    for path in dynamic_paths:
        create_route(path)
    return "已经动态生成路由"


# 动态路由生成: method1
def create_route(path: str):
    @app.get(path)
    async def dynamic_route():
        return {"message": f"This is the dynamic route for {path}"}


# 运行时动态添加路由
def add_dynamic_route(path: str, handler):
    app.add_api_route(
        path,
        handler,
        methods=["GET"],
    )


# 定义一个简单的 handler 函数
async def dynamic_handler():
    return {"message": "This is a dynamically added route"}


# 动态生成路由：method2
@app.get("/method")
def read_root():
    # 在运行时动态添加这个路由
    add_dynamic_route("/dynamic", dynamic_handler)
    return "已经动态生成路由"


def custom_handler(request):
    return PlainTextResponse("This is a custom route")


# 动态生成路由：method2
@app.get("/method2")
def read_root():
    # 在运行时动态添加这个路由 组件，
    # 本质就是添加 了一个路由组件
    # 使用 add_route 手动指定路径和 HTTP 方法
    app.add_route("/custom", custom_handler, methods=["GET"])
    return "已经动态生成路由"


# 直接python执行也行
if __name__ == "__main__":
    uvicorn.run("demo:app", host="127.0.0.1", port=5000, log_level="info", reload=False)
