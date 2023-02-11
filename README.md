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

必须要看表单验证模型

https://pydantic-docs.helpmanual.io/usage/types/

#### post验证模型

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

#### Query模型

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

#### Path模型

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

#### body模型

如果存在类文本格式的数据，我们确实需要body查询。

```
# !Body校验，不管传递啥，都是body类型
@router.put("/putBody/")
async def update_item(importance: str = Body()):
    results = {"importance": importance}
    return results


class Item3(BaseModel):
    name: str


# !body 特殊参数，一旦加入则必须使用嵌套对象
@router.put("/putBody2/{item_id}")
async def update_item2(item_id: int, item: Item3 = Body(embed=True)):
    results = {"item_id": item_id, "item": item}
    return results
```

#### Field模型验证

```
# !Field 具有Query全部的参数，不过引入的Pydantic中的
# ?请记住当你从 fastapi 导入 Query、Path 等对象时，他们实际上是返回特殊类的函数。
class Item4(BaseModel):
    name: str
    description: Union[str, None] = Field(default=None, title="The description of the item", max_length=300)
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: Union[float, None] = None


@router.put("/items4/{item_id}")
async def update_item3(item_id: int, item: Item4 = Body(embed=True)):
    results = {"item_id": item_id, "item": item}
    return results
```

#### nest嵌套模型+特殊模型

这种特殊的模型，都需要从pydantic和typing中继承。这两个库就是后端数据验证的核心。

```
# !申明具有子类型的嵌套模型
class Image(BaseModel):
    url: HttpUrl
    name: str
    # !引入特殊验证模型
    email: EmailStr
    data: Dict[str, str]
    data2: Tuple[str]
    data3: Set[int]


class TestApi(BaseModel):
    students: List[str] = []
    tags: Union[Set[str], None] = set()
    image: Union[Image, None] = None


@router.post("/testapi/")
async def postTestApi(item: TestApi):
    print(item)
    return item
```

#### docs模型

顺便申明例子。。。

```
# !甚至可以声明例子。。。
class cs(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None

    class Config:
        # 举例子区域
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            }
        }


@router.put("/cs/")
async def update_cs(item: cs):
    results = {"item": item}
    return results
```

#### 额外数据模型

通过以下两个库，应该可以找到大部分数据验证模型了。

https://fastapi.tiangolo.com/zh/tutorial/extra-data-types/

https://pydantic-docs.helpmanual.io/usage/types/

### cookie & headre

你可以像定义 `Query` 参数和 `Path` 参数一样来定义 `Cookie`， headre 参数。

```
# !cookie header 参数，难道只能内部解析？
@router.post("/headre/")
async def readCookie(__cf_bm: Union[str, None] = Cookie(default=None), user_agent: Union[str, None] = Header(default=None)):
    # header参数： convert_underscores=False，可以禁止下划线连字符的自动转换
    print(__cf_bm, "\n", user_agent, "\n")
    return {"cookie": __cf_bm, "user_agent": user_agent}

```

这种方法，有点low啊，非要形参解耦的方式获取参数。



### 响应模型

#### 1.利用模型过滤参数response_model

这里真的缺少了一个sql和nosql client链接器，一般我们从数据库中取出来的数据为：

多组数据： [{},{}]

一组数据：{}，[]

单个数据：value

至于想要具体什么结构的数据，还可以二次处理他们，然后返回给前端。

```
# !利用模型过滤参数
class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: Union[str, None] = None


class UserOut(BaseModel):
    username: str = "admin"
    email: EmailStr
    full_name: Union[str, None] = None


@router.post("/user/", response_model=UserOut)
async def create_user(user: UserIn) -> Any:
    return user
```

#### 2.忽略响应模型中的默认值

```
# !利用模型过滤参数
class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: Union[str, None] = None


class UserOut(BaseModel):
    # !可以给响应模型添加默认值
    username: str = "admin"
    email: EmailStr
    full_name: Union[str, None] = None


# 给响应数据端，设置了一个模型
@router.post("/user/", response_model=UserOut)
async def create_user(user: UserIn) -> Any:
    return user

# 这样一来就可以忽略响应模型中的默认值
@router.get("/user/", response_model=UserOut, response_model_exclude_unset=True)
async def get_user(user: UserIn) -> Any:
    return user
```

```
其他忽略方法:
https://pydantic-docs.helpmanual.io/usage/exporting_models/#modeldict 原生方法
response_model_exclude_defaults=True
response_model_exclude_none=True
```

```
高级方法：
from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: float = 10.5


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The Bar fighters", "price": 62, "tax": 20.2},
    "baz": {
        "name": "Baz",
        "description": "There goes my baz",
        "price": 50.2,
        "tax": 10.5,
    },
}


@app.get(
    "/items/{item_id}/name",
    response_model=Item,
    # 要导入的对象
    response_model_include={"name", "description"},
)
async def read_item_name(item_id: str):
    return items[item_id]


@app.get("/items/{item_id}/public", response_model=Item, 
# 要忽略的对象
response_model_exclude={"tax"})
async def read_item_public_data(item_id: str):
    return items[item_id]
```

#### 3.响应状态码

```
100 及以上状态码用于「消息」响应。你很少直接使用它们。具有这些状态代码的响应不能带有响应体。
200 及以上状态码用于「成功」响应。这些是你最常使用的。
200 是默认状态代码，它表示一切「正常」。
另一个例子会是 201，「已创建」。它通常在数据库中创建了一条新记录后使用。
一个特殊的例子是 204，「无内容」。此响应在没有内容返回给客户端时使用，因此该响应不能包含响应体。
300 及以上状态码用于「重定向」。具有这些状态码的响应可能有或者可能没有响应体，但 304「未修改」是个例外，该响应不得含有响应体。
400 及以上状态码用于「客户端错误」响应。这些可能是你第二常使用的类型。
一个例子是 404，用于「未找到」响应。
对于来自客户端的一般错误，你可以只使用 400。
500 及以上状态码用于服务器端错误。你几乎永远不会直接使用它们。当你的应用程序代码或服务器中的某些部分出现问题时，它将自动返回这些状态代码之一。
```

```
from fastapi import FastAPI, status

app = FastAPI()


@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(name: str):
    return {"name": name}
    
@app.post("/items/", status_code=201)
async def create_item(name: str):
    return {"name": name}
```

### 表单数据

很少见到表单数据form传递了，除了上下传文件这样的操作。

安装表单解析工具

```
pip install python-multipart
```

```
表单数据的「媒体类型」编码一般为 application/x-www-form-urlencoded。
但包含文件的表单编码为 multipart/form-data。
```

```
# !表单信息传递
@router.post("/login/")
async def login(username: str = Form(), password: str = Form()):
    return {"username": username}
```

#### 文件上传

https://fastapi.tiangolo.com/zh/tutorial/request-files/

##### 基础文件上传

```
# !上传文件接口，bytes会一直占用内存，
@router.post("/files/")
async def create_file(file: bytes = File()):
    return {"file_size": len(file)}


# !推荐使用，方法更多，占用内存少
@router.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    contents = await file.read()
    print(contents)
    return {"filename": file.filename}
```

##### 可选文件上传

```
from fastapi import FastAPI, File, UploadFile

app = FastAPI()


@app.post("/files/")
async def create_file(file: bytes | None = File(default=None)):
    if not file:
        return {"message": "No file sent"}
    else:
        return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile | None = None):
    if not file:
        return {"message": "No upload file sent"}
    else:
        return {"filename": file.filename}
```

##### 多文件上传

```
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.post("/files/")
async def create_files(files: list[bytes] = File()):
    return {"file_sizes": [len(file) for file in files]}


@app.post("/uploadfiles/")
async def create_upload_files(files: list[UploadFile]):
    return {"filenames": [file.filename for file in files]}


@app.get("/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)
```

#### 文件上传+表单数据

```
from fastapi import FastAPI, File, Form, UploadFile

app = FastAPI()


@app.post("/files/")
async def create_file(
    file: bytes = File(), fileb: UploadFile = File(), token: str = Form()
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }
```

依然是推荐UploadFile接收表单文件

### 响应异常

基本响应异常

```
# !处理异常HTTPException
@router.get("/err/{item_id}")
async def check_err(item_id: str):
    if item_id != "index":
        raise HTTPException(status_code=404, detail="err", headers={"X-Error": "???"})
    return "be ok"
```

#### 自定义响应异常

如果你觉得不够用的话，还可以自定义。这个太扯了。

https://fastapi.tiangolo.com/zh/tutorial/handling-errors/

### 路径操作配置

标签配置：如果不配置标签，则http://127.0.0.1:8000/docs# 生成的API文档会出现问题我，从router 到 url 等等。

#### 1.url标签

```
from typing import Set, Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    tags: Set[str] = set()


@app.post("/items/", response_model=Item, tags=["items"])
async def create_item(item: Item):
    return item


@app.get("/items/", tags=["items"])
async def read_items():
    return [{"name": "Foo", "price": 42}]


@app.get("/users/", tags=["users"])
async def read_users():
    return [{"username": "johndoe"}]
```

#### 2.router标签

![image-20230211165018848](readme.assets/image-20230211165018848.png)

#### 3.额外参数

基本描述

```
from typing import Set, Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    tags: Set[str] = set()


@app.post(
    "/items/",
    response_model=Item,
    summary="Create an item",
    description="Create an item with all the information, name, description, price, tax and a set of unique tags",
)
async def create_item(item: Item):
    return item
```

请求端描述

    """
    Create an item with all the information:
    
    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    """

```
from typing import Set, Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    tags: Set[str] = set()


@app.post("/items/", response_model=Item, summary="Create an item")
async def create_item(item: Item):
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    """
    return item
```

响应端描述

response_description="The created item",

```
from typing import Set, Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    tags: Set[str] = set()


@app.post(
    "/items/",
    response_model=Item,
    summary="Create an item",
    response_description="The created item",
)
async def create_item(item: Item):
    return item
```

弃用路径

```
from fastapi import FastAPI

app = FastAPI()


@app.get("/items/", tags=["items"])
async def read_items():
    return [{"name": "Foo", "price": 42}]


@app.get("/users/", tags=["users"])
async def read_users():
    return [{"username": "johndoe"}]


@app.get("/elements/", tags=["items"], deprecated=True)
async def read_elements():
    return [{"item_id": "Foo"}]
```

### json兼容编码器

其实有很多更快的json序列化库，可以去看看。

```
from datetime import datetime

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

fake_db = {}


class Item(BaseModel):
    title: str
    timestamp: datetime
    description: str | None = None


app = FastAPI()


@app.put("/items/{id}")
def update_item(id: str, item: Item):
    json_compatible_item_data = jsonable_encoder(item)
    fake_db[id] = json_compatible_item_data
```

### 小技巧

https://fastapi.tiangolo.com/zh/tutorial/body-updates/

一套数据更新技巧。尤其是在使用nosql数据库时。除了put更新数据，还可以使用`PATCH`来更新数据.

## 依赖项

有种前端hoocks的感觉，但是功能更强大，复用所有逻辑，可以用来路由拦截，鉴权，数据库链接等。







## 安全验证







## 中间件



#### CORS（跨域资源共享）

https://fastapi.tiangolo.com/zh/tutorial/cors/

## 数据库客户端

### 1.sql客户端

### 2.nosql客户端

### 3.其他计算

深度学习AI，消息中间件，任务中间件等等。





### 4.使用自带后台异步任务中间件

如果简单的话，就用自带的。难的话，就用celery。

https://fastapi.tiangolo.com/zh/tutorial/background-tasks/



## 文档元数据

让你的docs更好看？

https://fastapi.tiangolo.com/zh/tutorial/metadata/

文档可以直接本地存储成HTML下来，不涉及到本地资源。



## 静态文件代理

理论上不需要，只需要配置好nginx，然后托管静态文件即可。

https://fastapi.tiangolo.com/zh/tutorial/static-files/



## 测试

一般不需要测试，除非甲方有要求。

https://fastapi.tiangolo.com/zh/tutorial/testing/









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



### 大型项目构成

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









