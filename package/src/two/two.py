from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect, WebSocketException, status
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
@router.get("/linkSQL")
async def linksql():
    # data = await sqlClient.get_db("insert into demo(username, password)values('NieBar', '123123123')")
    data = await sqlClient.get_db("select * from demo")
    if data["status"] == 1:
        return HTMLResponse("<h1>%s</h1>" % data["data"].all(), status_code=200)
    else:
        raise HTTPException(500, "database error")


@router.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks, q: str = Depends(get_query)):
    message = f"message to {email}\n"
    background_tasks.add_task(write_log, message)
    # !支持多次任务
    # background_tasks.add_task(write_log, message)
    return {"message": "Message sent"}


"""
websocket操作
"""


# !有bug存在，/ws/ 和 /ws 是不同的表示
@router.websocket("/ws")
async def websocket1(websocket: WebSocket):
    await websocket.accept()
    while True:
        # 持续接收参数
        data = await websocket.receive_text()
        print("接收数据:", data)
        await websocket.send_text(f"{data}")


class ConnectionManager:
    def __init__(self):
        # websocket连接池
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, token):
        # 等待链接，由于存在token是以子协议的方式传递。我们也得走子协议
        await websocket.accept(subprotocol=token)
        # 将联入的客户端加入列表
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        # 删除客户端
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        # 单一客户端发送
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        # 这里就是广播了，给所有客户端发送
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


# 加入钩子，验证token是否正确.
async def get_cookie_or_token(websocket: WebSocket):
    # 通过子协议头获取token
    token = websocket.headers.get("sec-websocket-protocol")

    if token != "123":
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    return token


@router.websocket("/ws3/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int, token: str = Depends(get_cookie_or_token)):
    # 开始接收链接
    await manager.connect(websocket, token)
    try:
        while True:
            # 接收文本数据
            data = await websocket.receive_text()
            # 单数据
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    # 这里的异常才是关键
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # 谁出问题，谁挂断
        await manager.broadcast(f"Client #{client_id} left the chat")
