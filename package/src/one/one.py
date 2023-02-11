from fastapi import APIRouter, Path, Query, Body


# !强制类型验证
from pydantic import BaseModel
from typing import Union, List

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
async def update_item(importance: int = Body()):
    results = {"importance": importance}
    return results

# class Item(BaseModel):
#     name: str
#     description: Union[str, None] = None
#     price: float
#     tax: Union[float, None] = None

# !body 特殊参数，一旦加入则必须使用嵌套对象
# @router.put("/items/{item_id}")
# async def update_item(item_id: int, item: Item = Body(embed=True)):
#     results = {"item_id": item_id, "item": item}
#     return results
