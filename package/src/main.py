from fastapi import FastAPI

# 通过形参设置类型，可以直接进行表单验证
from typing import Union
from enum import Enum


from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response, JSONResponse, ORJSONResponse


# 导入路由包
from routers import index


app = FastAPI()

# !导入路由根组件，这里的做法，仿照的是vue和react
app.include_router(index.router)


# !代理css和js等静态文件. 设定html为true则自动加载index.html文件
app.mount("/assets", StaticFiles(html=True, directory="assets"), name="assets")
# http://127.0.0.1:8000/assets/


# *路径参数
@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}


# !同等路由下，顺序很重要
# @app.get("/items2/test")
# async def read_item2():
#     return {"item_id": 1}


# *如果传入不是int，则会返回错误
@app.get("/items2/{item_id}")
async def read_item3(item_id: int):
    return {"item_id": item_id}


# ?这种写法，有点ts的感觉了
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


# 传递path路径参数
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


# 临时数据
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


# !这里就是get传参的标准写法, 对应请求写法, http://127.0.0.1:8000/getPara/?skip=0&limit=10
@app.get("/getPara/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]


# !可选参数，路径+get传参的结合，使用Union则可以声明其是否是可选参数，类似ts .?
@app.get("/union/{item_id}")
async def read_item(item_id: str, q: Union[str, None] = None, short: bool = False):
    if q:
        return {"item_id": item_id, "q": q, "short": short}
    return {"item_id": item_id}


# ?一种穿插写法
# @app.get("/users/{user_id}/items/{item_id}")
# async def read_user_item(user_id: int, item_id: str, q: Union[str, None] = None, short: bool = False):
#     item = {"item_id": item_id, "owner_id": user_id}
#     if q:
#         item.update({"q": q})
#     if not short:
#         item.update({"description": "This is an amazing item that has a long description"})
#     return item


# ?needy，一个必需的 str 类型参数。
# ?skip，一个默认值为 0 的 int 类型参数。
# ?limit，一个可选的 int 类型参数。
# @app.get("/items/{item_id}")
# async def read_user_item(
#     item_id: str, needy: str, skip: int = 0, limit: Union[int, None] = None
# ):
#     item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
#     return item


# uvicorn main:app --reload
