#!/usr/bin/python
# -*- coding: utf-8 -*-


# 导入包
from fastapi import FastAPI, Body
from pywebio.platform.fastapi import webio_routes
from pywebio.input import input, FLOAT
from pywebio.output import put_text, put_buttons
from pywebio.platform.fastapi import asgi_app

# 实力一个应用
app = FastAPI()
subapp = asgi_app(lambda: put_text("hello from pywebio"))


def task_1():
    height = input("请输入你的身高(cm)：", type=FLOAT)
    put_buttons(["Go task 2"], onclick=printMessage(height))


def printMessage(text):
    print(text)


subapp1 = asgi_app(task_1)

app.mount("/tool", FastAPI(routes=webio_routes(task_1)))
app.mount("/tool2", subapp1)


# get传参
@app.get("/get")
def read_root():
    return {"Hello": "World"}


# Body post
@app.post("/post")
async def update_item(importance: str = Body()):
    results = {"importance": importance}
    return results
