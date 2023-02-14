from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from two import two
from one import one


"""
这里就是路由模块了
app.include_router(users.router)
app.include_router(items.router)
app.include_router(
    ! 组件对象
    admin.router,
    ! 组件路由的前缀
    prefix="/admin",
    ! 组件路由的分组，主要是在docs中有用
    tags=["admin"],
    ! 组件的依赖，过滤器or拦截器
    dependencies=[Depends(get_token_header)],
    ! 组件的响应
    responses={418: {"description": "I'm a teapot"}},
)
"""


router = APIRouter()


# !从这里代理其他路由，仿照前端vue react的那一套组件式写法
router.include_router(two.router, prefix="/two", tags=['two'])
router.include_router(one.router, prefix="/one", tags=['one'])


# !这里可以直接使用fast其他api，当然，我本人更推荐这里单纯的当一个路由
@router.get("/router/", tags=["router"])
async def read_users():
    return HTMLResponse("<h1>router路由</h1>")
