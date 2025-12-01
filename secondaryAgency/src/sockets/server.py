#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
socket 转为其他协议
"""

import asyncio
import json
from typing import Dict
from loguru import logger


class AsyncServer(object):
    name = "服务端"

    def __init__(self, host, port, receQueue):
        self.host = host
        self.port = port
        self.sendQueue = asyncio.Queue()
        self.receQueue = receQueue

    @classmethod
    def setName(cls, n: str):
        cls.name = n

    async def sendMsg(self, msg: Dict):
        """
        服务端要发给输入节点的内容
        """
        await self.sendQueue.put(json.dumps(msg).encode())

    async def sendLoop(self, w):
        """
        从意识空间 发送给 输入节点
        """
        try:
            while True:
                msg = await self.sendQueue.get()
                if not msg:
                    continue
                w.write(msg)
                await w.drain()
                self.sendQueue.task_done()
        except Exception as identifier:
            logger.info("输入节点 服务端 发送问题", identifier)
        finally:
            w.close()
            await w.wait_closed()

    async def receLoop(self, r):
        """
        从输入节点 发送给 意识空间
        """
        try:
            while True:
                data = await r.read(1024)
                if not data:
                    continue
                node = json.loads(data.decode())
                await self.receQueue.put(node)
        except Exception as identifier:
            logger.info("输入节点 服务端 接收问题", identifier)

    async def handle_echo(self, reader, writer):
        """
        回调构建
        """
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.sendLoop(writer))
            tg.create_task(self.receLoop(reader))

    async def createInit(self):
        self.server = await asyncio.start_server(self.handle_echo, self.host, self.port)
        self.task = asyncio.create_task(self.server.serve_forever())
        logger.info(f"输入节点 服务端建立 {self.host}:{self.port}")

    async def offConnect(self):
        """
        关闭服务端
        """
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.task.cancel()
            logger.info(f"输入节点 服务端关闭 {self.host}:{self.port}")
