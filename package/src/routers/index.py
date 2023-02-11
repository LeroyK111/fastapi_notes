from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from two import two
from one import one


"""
这里就是路由模块了
"""


router = APIRouter()


# !从这里代理其他路由，仿照前端vue react的那一套组件式写法
router.include_router(two.router, prefix="/two", tags=['two'])
router.include_router(one.router, prefix="/one", tags=['one'])


# !这里可以直接使用fast其他api，当然，我本人更推荐这里单纯的当一个路由
@router.get("/router/", tags=["router"])
async def read_users():
    return HTMLResponse("<h1>router路由</h1>")
