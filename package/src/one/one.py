from fastapi import APIRouter, Path, Query, Body, Cookie, Header, status, Form, File, UploadFile, HTTPException


# !强制类型验证
from pydantic import BaseModel, Field, HttpUrl, EmailStr

# !子类型扩展
from typing import Any, Union, List, Dict, Tuple, Set

router = APIRouter()


# !组件two路由
@router.get("/", tags=["one"])
async def read_users():
    return {"message": "这里是one路由"}


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


# ! Query 特殊参数，可以通过Query(x=y)等属性值，对传参进行其它校验，比如len长度。。。
@router.get("/query/")
async def read_items(q: Union[str, None] = Query(default=None, max_length=10, min_length=1)):
    # 默认值是default，字符串最大长度是50
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# !添加正则检测
@router.post("/reQuery/")
async def read_items2(q: Union[str, None] = Query(default=None, min_length=3, max_length=50, regex="^fixedquery$")):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# !申明必填值的两种方式
# @router.get("/items/")
# async def read_items(q: str = Query(min_length=3)):
#     results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results.update({"q": q})
#     return results


# @router.get("/items/")
# async def read_items(q: str = Query(default=..., min_length=3)):
#     results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results.update({"q": q})
#     return results

# !这里则是必须填none
# @router.get("/items/")
# async def read_items(q: Union[str, None] = Query(default=..., min_length=3)):
#     results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results.update({"q": q})
#     return results


# !填入对象也行
# from pydantic import Required
# @router.get("/items/")
# async def read_items(q: str = Query(default=Required, min_length=3)):
#     results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results.update({"q": q})
#     return results


# !get传入list，http://localhost:8000/items/?q=foo&q=bar
@router.get("/qList/")
async def read_qlist(q: Union[List[str], None] = Query(default=None, title="接口名称", description="接口描述")):
    query_items = {"q": q}
    return query_items


# ! alias支持假名 http://127.0.0.1:8000/items/?qList=foobaritems
# @router.get("/qList/")
# async def read_qlist(q: Union[List[str], None] = Query(default=None, title="接口名称", description="接口描述", alias="qList")):
#     query_items = {"q": q}
#     return query_items


# !标注废弃deprecated
# @router.get("/items/")
# async def read_items(
#     q: Union[str, None] = Query(
#         default=None,
#         alias="item-query",
#         title="Query string",
#         description="Query string for the items to search in the database that have a good match",
#         min_length=3,
#         max_length=50,
#         regex="^fixedquery$",
#         deprecated=True,
#     )
# ):
#     results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results.update({"q": q})
#     return results


# ! path路径校验,你可以声明与 Query 相同的所有参数，但却是路径形式
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


# !剩下的就是额外数据类型了，时间time，日期date，二进制bytes，唯一值UUID等等
# https://fastapi.tiangolo.com/zh/tutorial/extra-data-types/


# !cookie header 参数，难道只能内部解析？
@router.post("/headre/")
async def readCookie(__cf_bm: Union[str, None] = Cookie(default=None), user_agent: Union[str, None] = Header(default=None)):
    # header参数： convert_underscores=False，可以禁止下划线连字符的自动转换
    print(__cf_bm, "\n", user_agent, "\n")
    return {"cookie": __cf_bm, "user_agent": user_agent}


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


# !使用状态响应码
@router.post("/testResponseStatus/", status_code=201)
async def testResponseStatus(name: str):
    return {"name": name}


# !使用状态响应对象
# @router.post("/testResponseStatus/", status_code=status.HTTP_201_CREATED)
# async def testResponseStatus(name: str):
#     return {"name": name}


# !表单信息传递
@router.post("/login/")
async def login(username: str = Form(), password: str = Form()):
    return {"username": username}


"""
UploadFile 与 bytes 相比有更多优势：
使用 spooled 文件：
存储在内存的文件超出最大上限时，FastAPI 会把文件存入磁盘；
这种方式更适于处理图像、视频、二进制文件等大型文件，好处是不会占用所有内存；
可获取上传文件的元数据；
自带 file-like async 接口；
暴露的 Python SpooledTemporaryFile 对象，可直接传递给其他预期「file-like」对象的库。
"""


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


@router.post("/files2/")
async def upload_data_file(file: bytes = File(), fileb: UploadFile = File(), token: str = Form()):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }


# !处理异常HTTPException
@router.get("/err/{item_id}")
async def check_err(item_id: str):
    if item_id != "index":
        raise HTTPException(status_code=404, detail="err", headers={"X-Error": "???"})
    return "be ok"

