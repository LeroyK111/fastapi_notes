# FastAPI框架学习

## 为什么要选择fastapi框架

典型的MVC框架，FastAPI 是一个用于构建 API 的现代、快速（高性能）的 web 框架，使用 Python 3.6+ 并基于标准的 Python 类型提示。

1.可与 **NodeJS** 和 **Go** 并肩的极高性能web框架。（等我需要用到Rust时，可能会更快，😀）

2.自动生成接口文档。交互式 API 文档以及具探索性 web 界面。因为该框架是基于 OpenAPI，所以有很多可选项，FastAPI 默认自带两个交互式 API 文档。直接生成api文档，发给前端。

http://127.0.0.1:8000/docs

http://127.0.0.1:8000/redoc

类似Flask的写法，但是异步IO，性能得到了极大提高。

## 基本

安装方式：

全功能安装

```
$ pip install "fastapi[all]"
```

生产环境安装，这是体积最小的包了

```
$ pip install fastapi "uvicorn[standard]"
```

简单使用

```
# package/src/main.py

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

```

命令行，启动网关

```
$ uvicorn main:app --reload
```

 常用REST接口写法。其他method不常用

```
POST：创建数据。
GET：读取数据。
PUT：更新数据。
DELETE：删除数据。
```

### 路径

#### 路径传参

```
@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}
```

2.传参校验

```
# *如果传入不是int，则会返回错误
@app.get("/items2/{item_id}")
async def read_item3(item_id: int):
    return {"item_id": item_id}





# 枚举类型,这里就特别类似ts的接口写法了
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
```

3.路径顺序

```
# !同等路由下，顺序很重要
@app.get("/items2/test")
async def read_item2():
    return {"item_id": 1}


# *如果传入不是int，则会返回错误，进行传参的路由等级更高
@app.get("/items2/{item_id}")
async def read_item3(item_id: int):
    return {"item_id": item_id}
```

4.传递path路径参数

```
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}
```

#### get传参

1.基础

```
# !这里就是get传参的标准写法, 对应请求写法, http://127.0.0.1:8000/getPara/?skip=0&limit=10
@app.get("/getPara/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]
```

2.可选参数Union

```
@app.get("/union/{item_id}")
async def read_item(item_id: str, q: Union[str, None] = None, short: bool = False):
    if q:
        return {"item_id": item_id, "q": q, "short": short}
    return {"item_id": item_id}
```

3.混合写法

```
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
```

### 请求体

服务端获取request对象，验证request中header, body,data等参数的过程.

#### post表单验证

```
# src/one/one.py
# !接口写法
class Item(BaseModel):
    name: str
    # !可选属性
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None


@router.post("/postAuth/")
async def create_item(item: Item):
    # !我们访问一下对象的所有属性
    print(item)
    itemDict = item.dict()
    print(itemDict)
    return item


# ?这里就是组合式了
# @router.put("/postAuth/{item_id}")
# async def create_item2(item_id: int, item: Item, q: Union[str, None] = None):
#     result = {"item_id": item_id, **item.dict()}
#     if q:
#         result.update({"q": q})
#     return result
```

#### Query特殊查询

https://fastapi.tiangolo.com/zh/tutorial/query-params-str-validations/

常用于post和put

```
from typing import Union

from fastapi import FastAPI, Query

app = FastAPI()


@app.get("/items/")
async def read_items(
    q: Union[str, None] = Query(
        default=None, min_length=3, max_length=50, regex="^fixedquery$"
    )
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
```

#### Path特殊路径查询

使用接口的方式，根据url查询数据。

```
# ! 路径校验,你可以声明与 Query 相同的所有参数，但却是路径形式
# http://127.0.0.1:8000/one/path/123123?item-query=213
@router.get("/path/{item_id}")
async def read_path(
    item_id: int = Path(title="The ID of the item to get", gt=0, le=1000),
    q: Union[str, None] = Query(default=None, alias="item-query"),
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results
```









### 子路由











### 静态文件代理















## 启动服务

官网：https://www.uvicorn.org/		

设定指定serve运行ip和port

```
$ uvicorn main:app --host 0.0.0.0 --port 80
```

使用默认IP和端口，开启热重载

http://127.0.0.1:8000

```
$ uvicorn main:app --reload
```

其他指令，可以查询uvicorn官网。

```
$ uvicorn --help
```

网关和代理，可以是同一个事物，也可以不是。。。

![image-20230207225302497](readme.assets/image-20230207225302497.png)

网关服务：在操作系统上使用ip并创建对应的开放接口。通常是 LAN or localhost。

代理服务：端口转发，静态文件分发，限流，限速，负载均衡等功能。

**★具体生产部署，请看[部署](#部署) **

## 进阶

这里我们以一个项目package 结构为基准。我这里就直接使用前端的基本结构了

https://fastapi.tiangolo.com/tutorial/bigger-applications/#include-an-apirouter-with-a-prefix-tags-responses-and-dependencies

```
.
├── package              # "app" is a Python package
│   ├── __init__.py      # this file makes "app" a "Python package"
│   ├── main.py          # "main" module, e.g. import app.main
│   ├── dependencies.py  # "dependencies" module, e.g. import app.dependencies
│   └── routers          # "routers" is a "Python subpackage"
│   │   ├── __init__.py  # makes "routers" a "Python subpackage"
│   │   ├── items.py     # "items" submodule, e.g. import app.routers.items
│   │   └── users.py     # "users" submodule, e.g. import app.routers.users
│   └── internal         # "internal" is a "Python subpackage"
│       ├── __init__.py  # makes "internal" a "Python subpackage"
│       └── admin.py     # "admin" submodule, e.g. import app.internal.admin
```







## 其他

### 并发和并行

https://fastapi.tiangolo.com/zh/async/

多线程，多进程 = 并行

异步，协程 = 并发

二者可以相互叠加，提高serve的性能。

### 部署

目前因为微服务的成熟，更好的做法是cloud容器化，然后kubernetes，实现单容器单进程，然后使用弹性云网关进行反向代理。

#### 单服务器部署

https://gunicorn.org/

Gunicorn是uvicorn官方推荐的资源分配管理工具，可以帮助你分配进程，**同时这允许您动态地增加或减少工作进程的数量，从容地重启工作进程，或者在不停机的情况下执行服务器升级。**

（**Uvicorn**本身也有这个多进程启动的功能，但不全面。。。）

https://fastapi.tiangolo.com/zh/deployment/server-workers/





#### 多服务器部署

##### ★首要推荐**Kubernetes**

要多复杂由多复杂， 建议容器化，然后集群管理，使用弹性动态网关代理。

##### 免费云服务器

https://www.deta.sh/



### HTTPS证书

**ssl证书可以给nginx配置，也可以直接给serve配置，都行。**

一般一台服务器（单个ip）只能配置一张https证书。但TLS协议的扩展SNI，允许单ip对应多个证书，有兴趣可以了解一下，等于是ip复用了。









