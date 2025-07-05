"""
"中间件"是一个函数,它在每个请求被特定的路径操作处理之前,以及在每个响应返回之前工作.

它接收你的应用程序的每一个请求.
然后它可以对这个请求做一些事情或者执行任何需要的代码.
然后它将请求传递给应用程序的其他部分 (通过某种路径操作).
然后它获取应用程序生产的响应 (通过某种路径操作).
它可以对该响应做些什么或者执行任何需要的代码.
然后它返回这个响应.
"""
import time
from fastapi import Request


def plugs(app):
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        # 这里就是我自定义一个中间件
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response


