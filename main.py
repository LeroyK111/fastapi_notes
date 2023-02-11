# 引入类型提示
from typing import Union

# 导入包
from fastapi import FastAPI

# 解决跨域问题
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

# 实力一个应用
app = FastAPI()


origins = [
    # "http://localhost.tiangolo.com",
    # "https://localhost.tiangolo.com",
    # "http://localhost",
    # "http://localhost:8080",
    "*"
]

# 加入跨域中间件
app.add_middleware(
    CORSMiddleware,
    # 一个允许跨域请求的源列表
    allow_origins=origins,
    # 正则匹配url
    # allow_origin_regex= '*',
    # 指示跨域请求的cookie
    allow_credentials=True,
    # allow_methods 允许请求方式
    allow_methods=["*"],
    # 请求头列表,常见
    allow_headers=["*"],
    # 指示可以被浏览器访问的请求头
    # expose_headers=[],
    # 设定浏览器缓存 CORS 响应的最长时间
    # max_age=600
)


# 路由装饰器
@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


# 启动服务
# uvicorn main:app --reload

# 直接python执行也行
if __name__ == "__main__":
    uvicorn.run("example:app", host="127.0.0.1", port=5000, log_level="info")