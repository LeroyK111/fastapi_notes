from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from hooks import easy, Adv, sqlClient, nosqlClient
from Tasks.one import write_log, get_query


router = APIRouter()


"""
我们在这里使用钩子
"""


# !引入函数参数钩子
@router.get("/easy/")
async def read_users(commons: dict = Depends(easy.common_parameters)):
    print(commons)
    return {"message": "函数钩子"}


# !引入类参数钩子，可以不声明类
@router.get("/adv/")
async def read_users2(commons: Adv.CommonQueryParams = Depends(Adv.CommonQueryParams)):
    print(commons.__dict__)
    return {"message": "对象钩子"}


# !嵌套钩子, use_cache=False 是拒绝缓存钩子的意思，一般都是true
@router.get("/double/")
async def read_query(query_or_default: str = Depends(easy.query_or_cookie_extractor, use_cache=False)):
    return {"q_or_cookie": query_or_default}


# !无返回值，拦截装饰器。使用dependencies只是拦截而已，无所谓有没有返回值
@router.get("/Intercept/", dependencies=[Depends(easy.verify_token), Depends(easy.verify_key)])
async def read_items():
    return [{"item": "Foo"}, {"item": "Bar"}]


# !使用数据库钩子，操作数据
@router.get("/linkSQL/")
async def linksql():
    # data = await sqlClient.get_db("insert into demo(username, password)values('NieBar', '123123123')")
    data = await sqlClient.get_db("select * from demo")
    if data["status"] == 1:
        return HTMLResponse("<h1>%s</h1>" % data["data"].all(), status_code=200)
    else:
        raise HTTPException(500, "database error")


@router.post("/send-notification/{email}")
async def send_notification(
    email: str, background_tasks: BackgroundTasks, q: str = Depends(get_query)
):
    message = f"message to {email}\n"
    background_tasks.add_task(write_log, message)
    # !支持多次任务
    # background_tasks.add_task(write_log, message)
    return {"message": "Message sent"}



# 这里我们选择一个ssr渲染实现
